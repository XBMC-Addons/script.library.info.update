#import modules
import xbmc
import sys

### import libraries
from resources.lib.script_exceptions import NoFanartError
from resources.lib.utils import *
from operator import itemgetter

### get addon info
__localize__    = ( sys.modules[ "__main__" ].__localize__ )
__addon__    = ( sys.modules[ "__main__" ].__addon__ )

API_KEY = '4be68d7eab1fbd1b6fd8a3b80a65a95e'

def get_ratings(media_id):
    url = 'http://api.themoviedb.org/3/movie/%s?api_key=%s'
    api_data = get_data(url%(media_id, API_KEY), 'json')
    data = []
    if api_data == "Empty" or not api_data:
        return data
    else:
        # Get fanart
        try:
            data = {'rating': api_data.get('vote_average',''),
                    'votes': api_data.get('vote_count','')}
        except Exception, e:
            log( 'Problem report: %s' %str( e ), xbmc.LOGNOTICE )
        if data == []:
            log('No data for: %s' %media_id)
        else:
            return data

def get_releases(media_id):
    url = 'http://api.themoviedb.org/3/movie/%s/releases?api_key=%s'
    api_data = get_data(url%(media_id, API_KEY), 'json')
    data = []
    if api_data == "Empty" or not api_data:
        return data
    else:
        # Got through the list
        for item in api_data['countries']:
            #Check which one matches
            if item.get('iso_3166_1') == __addon__.getSetting("movie_cert_lang_tmdb").upper():
                # strip the date to only the year
                year, month, day = item.get('release_date','').split('-')
                data = {'mpaa': item.get('certification').upper(),
                        'iso_3166_1': item.get('iso_3166_1').upper(),
                        'year': year}
        if data == []:
            log('No data for: %s' %media_id)
        else:
            return data


def _search_movie(medianame,year=''):
    medianame = normalize_string(medianame)
    log('TMDB API search criteria: Title[''%s''] | Year[''%s'']' % (medianame,year) )
    illegal_char = ' -<>:"/\|?*%'
    for char in illegal_char:
        medianame = medianame.replace( char , '+' ).replace( '++', '+' ).replace( '+++', '+' )

    search_url = 'http://api.themoviedb.org/3/search/movie?query=%s+%s&api_key=%s' %( medianame, year, API_KEY )
    tmdb_id = ''
    log('TMDB API search:   %s ' % search_url)
    try:
        data = get_data(search_url, 'json')
        if data == "Empty":
            tmdb_id = ''
        else:
            for item in data['results']:
                if item['id']:
                    tmdb_id = item['id']
                    break
    except Exception, e:
        log( str( e ), xbmc.LOGERROR )
    if tmdb_id == '':
        log('TMDB API search found no ID')
    else:
        log('TMDB API search found ID: %s' %tmdb_id)
    return tmdb_id