import search
from search.core import porter_stemmer, startswith
from ias.models import Taxon, Sighting

search.register(Taxon, ('scientific_name', 'common_name', 'rank'),
    indexer=startswith, search_index='startswith_index')
search.register(Taxon, ('scientific_name', 'common_name', 'rank'),
    indexer=porter_stemmer, search_index='porterstemmer_index')
search.register(Sighting, ('email', 'taxon_name'), indexer=startswith, search_index='startswith_index')
search.register(Sighting, ('email', 'taxon_name'), indexer=porter_stemmer, search_index='porterstemmer_index')
