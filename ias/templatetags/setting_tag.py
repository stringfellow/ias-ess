from django import template
from django.conf import settings



register = template.Library()



class SettingNode(template.Node):
    def __init__(self, setting):
        self.setting = setting
    
    def render(self, context):
        try:
            setting_value = getattr(settings, self.setting)
        except AttributeError:
            return ""
        else:
            return setting_value


@register.tag
def setting(parser, token):
    bits = token.split_contents()
    return SettingNode(bits[1])
    