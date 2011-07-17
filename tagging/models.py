"""
Models and managers for generic tagging.
"""
import types

# Python 2.3 compatibility
try:
    set
except NameError:
    from sets import Set as set

from django.db import models
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from tagging import settings
from tagging.utils import calculate_cloud, get_tag_list, get_queryset_and_model, parse_tag_input
from tagging.utils import LOGARITHMIC

############
# Managers #
############

class TagManager(models.Manager):
    def update_tags(self, obj, tag_names):
        """
        Update tags associated with an object.
        """
        ctype = ContentType.objects.get_for_model(obj)

        ##TODO: This fails silently in non-rel when it should not
        #current_tags = list(self.filter(items__content_type__pk=ctype.pk,
        #                                items__object_id=obj.pk))
        ##This works, divided into two queries
        items = TaggedItem.objects.filter(content_type__pk=ctype.pk, object_id=obj.pk)
        current_tags = self.filter(pk__in=[item.tag_id for item in items])

        updated_tag_names = parse_tag_input(tag_names)
        if settings.FORCE_LOWERCASE_TAGS:
            updated_tag_names = [t.lower() for t in updated_tag_names]

        # Remove tags which no longer apply
        tags_for_removal = [tag for tag in current_tags \
                            if tag.name not in updated_tag_names]
        if len(tags_for_removal):
            TaggedItem._default_manager.filter(content_type__pk=ctype.pk,
                                               object_id=obj.pk,
                                               tag__in=tags_for_removal).delete()
        # Add new tags
        current_tag_names = [tag.name for tag in current_tags]
        for tag_name in updated_tag_names:
            if tag_name not in current_tag_names:
                tag, created = self.get_or_create(name=tag_name)
                TaggedItem._default_manager.create(tag=tag, object=obj)
               
    def add_tag(self, obj, tag_name):
        """
        Associates the given object with a tag.
        """
        tag_names = parse_tag_input(tag_name)
        if not len(tag_names):
            raise AttributeError(_('No tags were given: "%s".') % tag_name)
        if len(tag_names) > 1:
            raise AttributeError(_('Multiple tags were given: "%s".') % tag_name)
        tag_name = tag_names[0]
        if settings.FORCE_LOWERCASE_TAGS:
            tag_name = tag_name.lower()
        tag, created = self.get_or_create(name=tag_name)
        ctype = ContentType.objects.get_for_model(obj)
        TaggedItem._default_manager.get_or_create(
            tag=tag, content_type=ctype, object_id=obj.pk)

    def get_for_object(self, obj):
        """
        Create a queryset matching all tags associated with the given
        object.
        """
        ctype = ContentType.objects.get_for_model(obj)
        ##TODO: This fails silently in non-rel when it should not
        #return self.filter(items__content_type__pk=ctype.pk,
        #                   items__object_id=obj.pk)
        ##This works, divided into two queries
        items = TaggedItem.objects.filter(content_type__pk=ctype.pk, object_id=obj.pk)
        tags = self.filter(pk__in=[item.tag_id for item in items])
        return tags

    def usage_for_model(self, model, counts=False, min_count=None, filters=None):
        """
        Obtain a list of tags associated with instances of the given
        Model class.

        If ``counts`` is True, a ``count`` attribute will be added to
        each tag, indicating how many times it has been used against
        the Model class in question.

        If ``min_count`` is given, only tags which have a ``count``
        greater than or equal to ``min_count`` will be returned.
        Passing a value for ``min_count`` implies ``counts=True``.

        To limit the tags (and counts, if specified) returned to those
        used by a subset of the Model's instances, pass a dictionary
        of field lookups to be applied to the given Model as the
        ``filters`` argument.
        """

        if filters is None: 
            ctype = ContentType.objects.get_for_model(model)
            if min_count is not None:
                modeltags = ModelTags._default_manager.filter(content_type=ctype, 
                                                              count__gte=min_count) \
                                                      .order_by('-count')
            else:
                modeltags = ModelTags._default_manager.filter(content_type=ctype) \
                                                      .order_by('-count')
            tags = []
            for modeltag in modeltags:
                new_tag = self.model(id=modeltag.tag_id, name=modeltag.tag_name)
                if counts or min_count:
                    new_tag.count = modeltag.count
                tags.append(new_tag)
            return tags

        queryset = model._default_manager.filter()
        for f in filters.items():
            queryset.query.add_filter(f)
        tags = self.usage_for_queryset(queryset, counts, min_count)

        return tags 

    def usage_for_queryset(self, queryset, counts=False, min_count=None):
        """
        Obtain a list of tags associated with instances of a model
        contained in the given queryset.

        If ``counts`` is True, a ``count`` attribute will be added to
        each tag, indicating how many times it has been used against
        the Model class in question.

        If ``min_count`` is given, only tags which have a ``count``
        greater than or equal to ``min_count`` will be returned.
        Passing a value for ``min_count`` implies ``counts=True``.
        """
        ## Nonrel requires two queries and in-memory aggregation and sorting

        ## (1) execute the query defined by the queryset, in order to get the pks
        ## TODO: using set instead of a simple list comprehension because of 
        ## a limitation of django-nonrel, where the __in operator creates duplicates
        pks = set()
        for obj in queryset.all():
            pks.add(obj.pk)

        ## (2) grab all TaggedItems that point to the pks from the queryset
        ctype = ContentType.objects.get_for_model(queryset.model)
        items = TaggedItem._default_manager.filter(content_type=ctype, object_id__in=pks)
        
        ## if there are no TaggedItems at all that point to the pks, then there are no tags
        if len(items) == 0:
            return []

        ## (3) Simulate SQL aggregation in memory.
        return self._package_and_sort(items, counts, min_count)


    def related_for_model(self, tags, model, counts=False, min_count=None):
        """
        Obtain a list of tags related to a given list of tags - that
        is, other tags used by items which have all the given tags.

        If ``counts`` is True, a ``count`` attribute will be added to
        each tag, indicating the number of items which have it in
        addition to the given list of tags.

        If ``min_count`` is given, only tags which have a ``count``
        greater than or equal to ``min_count`` will be returned.
        Passing a value for ``min_count`` implies ``counts=True``.
        """
        ## Nonrel requires two (maybe three) queries and in-memory aggregation and sorting

        ## (1) grab all of the object_ids that point to the specified tags, for the model
        object_ids = TaggedItem.objects._get_intersection_object_ids(model, tags)

        ## (2) grab all of the TaggedItems that point to the same objects
        content_type = ContentType.objects.get_for_model(model)
        related = TaggedItem._default_manager.filter(object_id__in=object_ids, 
                                                     content_type=content_type)

        ## if there are no related TaggedItems at all, then there are no related tags
        if len(list(related)) == 0: ## TODO: django-nonrel len() bug
            return []

        ## (3) Simulate SQL aggregation in memory, and exclude the original tags.
        exclude_ids = set()
        for tag in get_tag_list(tags): #this may, or may not, execute an additional query
            exclude_ids.add(tag.id)
        return self._package_and_sort(related, counts, min_count, exclude_ids)

    def _package_and_sort(self, items, counts, min_count, exclude_ids=None):
        """
        This method is a nonrel stand-in for aggregation.
        """
        ## perform the aggregation here in memory (horrible if there are many items)
        pk_map = {}
        for item in items:
            if exclude_ids is not None and item.tag_id in exclude_ids:
                continue

            name, count, tag_obj = pk_map.get(item.tag_id, ("", 0, None))
            count += 1

            if tag_obj is None:
                name = item.tag_name
                tag_obj = self.model(id=item.tag_id, name=name)
            elif name != item.tag_name:
                raise Exception("The tag_name and tag_id of item '%s' don't match." % item)
            elif name != tag_obj.name:
                raise Exception("Name of tag '%s' doesn't match expected value." % tag_obj)

            if counts or min_count:
                tag_obj.count = count
            pk_map[item.tag_id] = (name, count, tag_obj)

        ## sort and filter the outcome (sort might not be necessary; 'filter' is not optimal)
        if counts or min_count:
            tags = sorted(pk_map.items(), key=lambda item: item[1][1], reverse=True)
            if min_count:
               tags = [item[1][2] for item in tags if item[1][1] >= min_count]
            else:
               tags = [item[1][2] for item in tags] 
        else:
            tags = [pk_map[item][2] for item in pk_map]
        return tags

    def cloud_for_model(self, model, steps=4, distribution=LOGARITHMIC,
                        filters=None, min_count=None):
        """
        Obtain a list of tags associated with instances of the given
        Model, giving each tag a ``count`` attribute indicating how
        many times it has been used and a ``font_size`` attribute for
        use in displaying a tag cloud.

        ``steps`` defines the range of font sizes - ``font_size`` will
        be an integer between 1 and ``steps`` (inclusive).

        ``distribution`` defines the type of font size distribution
        algorithm which will be used - logarithmic or linear. It must
        be either ``tagging.utils.LOGARITHMIC`` or
        ``tagging.utils.LINEAR``.

        To limit the tags displayed in the cloud to those associated
        with a subset of the Model's instances, pass a dictionary of
        field lookups to be applied to the given Model as the
        ``filters`` argument.

        To limit the tags displayed in the cloud to those with a
        ``count`` greater than or equal to ``min_count``, pass a value
        for the ``min_count`` argument.
        """
        tags = list(self.usage_for_model(model, counts=True, filters=filters,
                                         min_count=min_count))
        return calculate_cloud(tags, steps, distribution)


class TaggedItemManager(models.Manager):
    """
    Note from original (SQL-relational) version:
    FIXME There's currently no way to get the ``GROUP BY`` and ``HAVING``
          SQL clauses required by many of this manager's methods into
          Django's ORM.

          For now, we manually execute a query to retrieve the PKs of
          objects we're interested in, then use the ORM's ``__in``
          lookup to return a ``QuerySet``.

          Now that the queryset-refactor branch is in the trunk, this can be
          tidied up significantly.

    This note is somewhat irrelivant for this non-relational implementation,
    as non-relational systems often do not include group-by and having concepts,
    especially google app engine, which this implementation is targeting.
    """

    def get_by_model(self, queryset_or_model, tags):
        """
        Create a ``QuerySet`` containing instances of the specified
        model associated with a given tag or list of tags.

        Nonrel note: I don't know why the original was using 
        get_intersection_by_model here.  get_union_by_model would
        be more efficient from a non-rel perspective, and seems 
        just as valid.
        """
        return self.get_intersection_by_model(queryset_or_model, tags)

    def get_intersection_by_model(self, queryset_or_model, tags):
        """
        Create a ``QuerySet`` containing instances of the specified
        model associated with *all* of the given list of tags.

        Because get_intersection_by_model requires an in-memory
        aggregation impelementation, it is less efficient than 
        get_union_by_model.
        """
        queryset, model = get_queryset_and_model(queryset_or_model)
        object_ids = self._get_intersection_object_ids(model, tags)

        if len(object_ids) > 1:
            return queryset.filter(pk__in=object_ids)
        elif len(object_ids) == 1:
            return queryset.filter(pk=object_ids[0])
        else:
            return model._default_manager.none()

    def _get_intersection_object_ids(self, model, tags):
        """
        Returns a list of the object ids of all items for a given model that 
        intersect with the given tags.
        """
        content_type = ContentType.objects.get_for_model(model)

        items = self._get_item_list(tags, content_type)
        items_count = len(list(items)) ## TODO: django-nonrel len() bug
        if items_count > 1:
            tag_count = self._get_tag_count(tags)
            pd_map = {}
            for item in items:
                count = pd_map.get(item.object_id, 0)
                pd_map[item.object_id] = count + 1

            return [object_id for object_id in pd_map if pd_map[object_id] == tag_count]

        elif items_count == 1:
            return [items[0].object_id]

        else:
             return []

    def get_union_by_model(self, queryset_or_model, tags):
        """
        Create a ``QuerySet`` containing instances of the specified
        model associated with *any* of the given list of tags.

        get_union_by_model is more efficent than get_intersection_by_model.
        """
        queryset, model = get_queryset_and_model(queryset_or_model)
        content_type = ContentType.objects.get_for_model(model)

        items = self._get_item_list(tags, content_type)

        ## TODO: This does not work, because when the same item has
        ## several of the tags supplied, that item's id shows up twice.
        ## This is not standard django behavior, and is specific to gae
        #object_ids = [item.object_id for item in items]
        ## This works, however
        object_ids = set()
        for item in items:
            object_ids.add(item.object_id)

        if len(object_ids) > 0:
            return queryset.filter(pk__in=object_ids)
        elif len(object_ids) == 1:
            return queryset.filter(pk=items[0].object_id)
        else:
            return model._default_manager.none()

    def _get_tag_count(self, tags):
        if isinstance(tags, Tag):
            return 1
        elif isinstance(tags, QuerySet) and tags.model is Tag:
            ##TODO: for some reason this doesn't work
            #return len(tags)
            ## But this does!
            return len(list(tags))
        elif isinstance(tags, types.StringTypes):
            return len(parse_tag_input(tags))
        elif isinstance(tags, (types.ListType, types.TupleType)):
            return len(tags)

    def _get_item_list(self, tags, content_type):
        """
        Implemented for nonrel to take advantage of denormalization between 
        Tag and TaggedItem.

        Utility function for accepting tag input in a flexible manner, and using
        it to generate a list of items that use that tag, given a specific content type.

        If a ``Tag`` object is given, it will be returned in a list as
        its single occupant.

        If given, the tag names in the following will be used to create a
        ``Tag`` ``QuerySet``:

           * A string, which may contain multiple tag names.
           * A list or tuple of strings corresponding to tag names.
           * A list or tuple of integers corresponding to tag ids.

        If given, the following will be returned as-is:

           * A list or tuple of ``Tag`` objects.
           * A ``Tag`` ``QuerySet``.

        """
        if isinstance(tags, Tag):
            return self.filter(tag=tags, content_type=content_type)
        elif isinstance(tags, QuerySet) and tags.model is Tag:
            ## TODO: is this a nonrel bug? Shouldn't tag__in iterate over the tags on its own?
            return self.filter(tag__in=[tag for tag in tags], content_type=content_type)
        elif isinstance(tags, types.StringTypes):
            return self.filter(tag_name__in=parse_tag_input(tags), 
                               content_type=content_type)
        elif isinstance(tags, (types.ListType, types.TupleType)):
            if len(tags) == 0:
                return []
            if len(tags) == 1:
                if isinstance(tags[0], types.StringTypes):
                    return self.filter(tag_name=force_unicode(tags[0]), 
                                       content_type=content_type)
                elif isinstance(tags[0], Tag):
                    return self.filter(tag=tags[0], content_type=content_type)
                elif isinstance(tags[0], (types.IntType, types.LongType)):
                    return self.filter(tag_id=tags[0], content_type=content_type)
            contents = set()
            for item in tags:
                if isinstance(item, types.StringTypes):
                    contents.add('string')
                elif isinstance(item, Tag):
                    contents.add('tag')
                elif isinstance(item, (types.IntType, types.LongType)):
                    contents.add('int')
            if len(contents) == 1:
                if 'string' in contents:
                    return self.filter(tag_name__in=[force_unicode(tag) for tag in tags], 
                                       content_type=content_type)
                elif 'tag' in contents:
                    return self.filter(tag__in=tags, content_type=content_type)
                elif 'int' in contents:
                    return self.filter(tag_id__in=tags, content_type=content_type)
            else:
                raise ValueError(_('If a list or tuple of tags is provided, they '
                                   'must all be tag names, Tag objects or Tag ids.'))
        else:
            raise ValueError(_('The tag input given was invalid.'))

    def get_related(self, obj, queryset_or_model, num=None):
        """
        Retrieve a list of instances of the specified model which share
        tags with the model instance ``obj``, ordered by the number of
        shared tags in descending order.

        If ``num`` is given, a maximum of ``num`` instances will be
        returned.
        """
        queryset, model = get_queryset_and_model(queryset_or_model)

        ## (1) Query 1, grab the items for the specified object
        content_type = ContentType.objects.get_for_model(obj)
        obj_items = self.filter(content_type=content_type, object_id=obj.pk)

        ## (2) Query 2, grab the items that share the same tags as that first list
        if not isinstance(obj, model):
            content_type = ContentType.objects.get_for_model(model)
            tag_ids = [item.tag_id for item in obj_items]
            tag_items = self.filter(content_type=content_type, tag__pk__in=tag_ids)
        else:
            tag_ids = [item.tag_id for item in obj_items]
            tag_items = self.filter(content_type=content_type, tag__pk__in=tag_ids) \
                            .exclude(object_id=obj.pk)

        ## (3) Aggregate and sort the results
        pk_map = {}
        ## TODO: This if test is required because of a bug in django-nonrel
        ## where empty iterators raise IndexErrors (in djangoappengine/db/compiler.py:285). 
        ## I put tag_items in a list because of another django-nonrel bug.
        tag_items = list(tag_items)
        if len(tag_items) > 0:
            for item in tag_items:
                count = pk_map.get(item.object_id, 0)
                pk_map[item.object_id] = count + 1

            object_ids = sorted(pk_map.keys(), key=lambda k: pk_map[k], reverse=True)
            if num is not None:
                object_ids = object_ids[0:num]
        else:
            return []
        
        ## (4) Create the final list of sorted objects
        if len(object_ids) > 0:
            # Use in_bulk here instead of an id__in lookup, because id__in would
            # clobber the ordering.
            object_dict = queryset.in_bulk(object_ids)
            ## TODO: using int() here because in_bulk somehow is changing the id to int.
            ## My concern is that this behavior may be specific to gae -legutierr
            return [object_dict[int(object_id)] for object_id in object_ids \
                    if int(object_id) in object_dict]
        else:
            return []

##########
# Models #
##########

class Tag(models.Model):
    """
    A tag.
    """
    name = models.CharField(_('name'), max_length=50, unique=True, db_index=True)

    objects = TagManager()

    class Meta:
        ordering = ('name',)
        verbose_name = _('tag')
        verbose_name_plural = _('tags')

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Tag, self).save(*args, **kwargs)
        for model_tag in self.model_tags.all():
            if model_tag.tag_name != self.name:
                model_tag.tag_name = self.name
                model_tag.save()

        for item in self.items.all():
            if item.tag_name != self.name:
                item.tag_name = self.name
                item.save()
        

class ModelTags(models.Model):
    """
    Keeps the count of all the times that a given tag is used for a given content_type/
    model. This denormalization is necessary in order to generate faster lookups 
    """
    tag          = models.ForeignKey(Tag, verbose_name=_('tag'), related_name='model_tags')
    tag_name     = models.CharField(_('tag name'), max_length=50, db_index=True)
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'))
    count        = models.PositiveIntegerField(default=0)

    def get_model(self):
        self.content_type.__class__.model_class()

    class Meta:
        # Enforce unique tag association per object
        unique_together = (('tag', 'content_type',),)
        verbose_name = _('model tags')
        verbose_name_plural = _('model tags')

    def __unicode__(self):
        return u'%s [%s]' % (self.object, self.tag)

    def save(self, *args, **kwargs):
        if self.tag_name is None or self.tag_name == "":
            self.tag_name = self.tag.name

        super(ModelTags, self).save(*args, **kwargs)


class TaggedItem(models.Model):
    """
    Holds the relationship between a tag and the item being tagged.
    """
    tag          = models.ForeignKey(Tag, verbose_name=_('tag'), related_name='items')
    tag_name     = models.CharField(_('tag name'), max_length=50, db_index=True)
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'))
    # TODO: does this have to be a CharField to work on non-rel?
    object_id    = models.CharField(_('object id'), db_index=True, max_length=100)
    object       = generic.GenericForeignKey('content_type', 'object_id')
    model_tag    = models.ForeignKey(ModelTags, verbose_name=_('model count'))

    objects = TaggedItemManager()

    class Meta:
        # Enforce unique tag association per object
        unique_together = (('tag', 'content_type', 'object_id'),)
        verbose_name = _('tagged item')
        verbose_name_plural = _('tagged items')

    def __unicode__(self):
        return u'%s [%s]' % (self.object, self.tag)

    def save(self, *args, **kwargs):
        if not self.id or self.model_tag is None:
            model_tag, created = \
                 ModelTags._default_manager.get_or_create(tag=self.tag, 
                                                          content_type=self.content_type)
            model_tag.count += 1
            model_tag.save()
            self.model_tag = model_tag

        elif self.model_tag.tag.pk != self.tag.pk:
            model_tag, created = \
                 ModelTags._default_manager.get_or_create(tag=self.tag,
                                                          content_type=self.content_type)
            model_tag.count += 1
            model_tag.save()

            old_model_tag = self.model_tag
            self.model_tag = model_tag

            old_model_tag.count -= 1
            if old_model_tag.count == 0:
                old_model_tag.delete()
            else:
                old_model_tag.save()

        if self.tag_name is None or self.tag_name == "":
            self.tag_name = self.tag.name
                
        super(TaggedItem, self).save(*args, **kwargs)

