#import modules
import xbmc
import sys

### import libraries
from resources.lib.script_exceptions import NoFanartError
from resources.lib.utils import *
from operator import itemgetter
from xml.parsers.expat import ExpatError

### get addon info
__localize__    = ( sys.modules[ "__main__" ].__localize__ )
__addon__    = ( sys.modules[ "__main__" ].__addon__ )


def get_ratings(media_id):
    url = 'http://www.imdbapi.com/?i=%s'
    api_data = get_data(url%(media_id), 'json')
    data = []
    if api_data == "Empty" or not api_data:
        return data
    else:
        # Get fanart
        try:
            data = {'rating': api_data.get('imdbRating',''),
                    'votes': api_data.get('imdbVotes',''),
                    'mpaa': api_data.get('Rated','')}
            if data['rating'] == 'N/A':
                data['rating'] = ''
        except Exception, e:
            log( 'Problem report: %s' %str( e ), xbmc.LOGNOTICE )
        if data == []:
            log('No data for: %s' %media_id)
        else:
            return data