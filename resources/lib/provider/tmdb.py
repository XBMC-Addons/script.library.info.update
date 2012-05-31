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
API_URL = 'http://api.themoviedb.org/3/movie/%s/images?api_key=%s'
BASE_IMAGEURL = "http://cf2.imgobject.com/t/p/"

class TMDBProvider():

    def __init__(self):
        self.name = 'TMDB'

    def get_image_list(self, media_id):
        data = get_data(API_URL%(media_id, API_KEY), 'json')
        image_list = []
        if data == "Empty" or not data:
            return image_list
        else:
            # Get fanart
            try:
                for item in data['backdrops']:
                    if int(item.get('vote_count')) >= 1:
                        rating = float( "%.1f" % float( item.get('vote_average'))) #output string with one decimal
                        votes = item.get('vote_count','n/a')
                    else:
                        rating = 'n/a'
                        votes = 'n/a'
                    image_list.append({'url': BASE_IMAGEURL + 'original' + item['file_path'],
                                       'preview': BASE_IMAGEURL + 'w300' + item['file_path'],
                                       'id': item.get('file_path').lstrip('/').replace('.jpg', ''),
                                       'type': ['fanart','extrafanart'],
                                       'height': item.get('height'),
                                       'width': item.get('width'),
                                       'language': item.get('iso_639_1','n/a'),
                                       'rating': rating,
                                       'votes': votes})
            except Exception, e:
                log( 'Problem report: %s' %str( e ), xbmc.LOGNOTICE )
            # Get posters
            try:
                for item in data['posters']:
                    if int(item.get('vote_count')) >= 1:
                        rating = float( "%.1f" % float( item.get('vote_average'))) #output string with one decimal
                        votes = item.get('vote_count','n/a')
                    else:
                        rating = 'n/a'
                        votes = 'n/a'
                    # Fill list
                    image_list.append({'url': BASE_IMAGEURL + 'original' + item['file_path'],
                                       'preview': BASE_IMAGEURL + 'w185' + item['file_path'],
                                       'id': item.get('file_path').lstrip('/').replace('.jpg', ''),
                                       'type': ['poster'],
                                       'height': item.get('height'),
                                       'width': item.get('width'),
                                       'language': item.get('iso_639_1','n/a'),
                                       'rating': rating,
                                       'votes': votes})
            except Exception, e:
                log( 'Problem report: %s' %str( e ), xbmc.LOGNOTICE )
            if image_list == []:
                raise NoFanartError(media_id)
            else:
                # Sort the list before return. Last sort method is primary
                image_list = sorted(image_list, key=itemgetter('rating'), reverse=True)
                image_list = sorted(image_list, key=itemgetter('language'))
                return image_list

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
    url = 'http://api.themoviedb.org/3/movie/%s/releases?api_key=%s&language=%s'
    api_data = get_data(url%(media_id, API_KEY, __addon__.getSetting("movie_cert_lang_tmdb") == '0'), 'json')
    data = []
    if api_data == "Empty" or not api_data:
        return data
    else:
        # Got through the list
        for item in api_data['countries']:
            #Check which one matches
            if item.get('iso_3166_1') == 'US':
                # strip the date to only the year
                year, month, day = item.get('release_date','').split('-')
                data = {'mpaa': item.get('certification'),
                        'iso_3166_1': item.get('iso_3166_1'),
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