#import modules
import re
import os
import sys
import xbmc
import xbmcaddon
import xbmcgui
import time

### get addon info
__addon__       = xbmcaddon.Addon(id='script.library.info.update')
__addonid__     = __addon__.getAddonInfo('id')
__addonname__   = __addon__.getAddonInfo('name')
__author__      = __addon__.getAddonInfo('author')
__version__     = __addon__.getAddonInfo('version')
__addonpath__   = __addon__.getAddonInfo('path')
__addonprofile__= xbmc.translatePath(__addon__.getAddonInfo('profile')).decode('utf-8')
__icon__        = __addon__.getAddonInfo('icon')
__localize__    = __addon__.getLocalizedString

from resources.lib.utils import *
from resources.lib.media_setup import __get_library as get_library
from resources.lib.media_setup import __set_library as set_library
from resources.lib.provider import tmdb
from resources.lib.provider import imdb
from resources.lib.script_exceptions import *
from xml.parsers.expat import ExpatError
from resources.lib.fileops import fileops

class Main:

    def __init__(self):
        if dialog_msg('yesno',
                      line1 = __localize__(32015),
                      line2 = __localize__(32016),
                      background = False,
                      nolabel = __localize__(32014),
                      yeslabel = __localize__(32013)):
            try:
                # Creates temp folder
                fileops()
            except CreateDirectoryError, e:
                log('Could not create directory: %s' % str(e))
                return False
            else:
                if __addon__.getSetting("movie_enable") == 'true':
                    media_list = get_medialist('movie')
                    if media_list:
                        update_movie(media_list)
            dialog_msg("close")


### retrieve list from library
def get_medialist(media_type):
    return get_library(media_type)


def update_movie(movie_list):
    processeditems = 0
    totalitems = len(movie_list)
    dialog_msg('create', line1 = 'Library info update', background = False)
    # Walk through media list
    for item in movie_list:
        new_info = {'imdbnumber': 'null',
            'title': 'null',
            'playcount': 'null',
            'runtime': 'null',
            'director': 'null',
            'studio': 'null',
            'year': 'null',
            'plot': 'null',
            'genre': 'null',
            'rating': 'null',
            'mpaa': 'null',
            'imdbnumber': 'null',
            'votes': 'null',
            'lastplayed': 'null',
            'originaltitle': 'null',
            'trailer': 'null',
            'tagline': 'null',
            'plotoutline': 'null',
            'writer': 'null',
            'country': 'null',
            'top250': 'null',
            'sorttitle': 'null',
            'set': 'null',
            'showlink': 'null'}
        if xbmc.abortRequested or dialog_msg('iscanceled'):
            log('XBMC abort requested, aborting')
            break
        dialog_msg('update',
                   percentage = int(processeditems / totalitems * 100.0),
                   line1 = '%s %s / %s' %(__localize__(32017), processeditems, totalitems),
                   line2 = item['name'],
                   background = False)
        
        #Check for IMDB id
        update_media = False
        if item['imdbnumber'].startswith('tt'):
            log('------------')
            log(item['name'])
            # Handle themoviedb.org
            if __addon__.getSetting(id="movie_rating") == 'themoviedb.org':
                data_rating = ''
                errmsg = ''
                try:
                    data_rating = tmdb.get_ratings(item['imdbnumber'])
                except HTTP404Error, e:
                    errmsg = '404: File not found'
                    data_result = 'skipping'
                except HTTP503Error, e:
                    errmsg = '503: API Limit Exceeded'
                    data_result = 'retrying'
                except ItemNotFoundError, e:
                    errmsg = '%s not found' % item['name']
                    data_result = 'skipping'
                except ExpatError, e:
                    errmsg = 'Error parsing xml: %s' % str(e)
                    data_result = 'retrying'
                except HTTPTimeout, e:
                    errmsg = 'Timed out'
                    data_result = 'skipping'
                except DownloadError, e:
                    errmsg = 'Possible network error: %s' % str(e)
                    data_result = 'skipping'
                else:
                    pass
                if errmsg:
                    log(errmsg)
                if data_rating:
                    #item['rating'] = float("%.1f" % float(item['rating']))
                    #data_rating['rating'] = float("%.1f" % float(data_rating['rating']))
                    #if item['rating'] < data_rating['rating']:
                    if item['votes'] < data_rating['votes']:
                        log('new rating: %s, old rating: %s' %(data_rating['rating'], item['rating']))
                        log('new votes: %s, old votes: %s' %(data_rating['votes'], item['votes']))
                        new_info['rating'] = float(data_rating['rating'])
                        new_info['votes'] = '"%s"' %data_rating['votes']
                        update_media = True
            
            if __addon__.getSetting(id="movie_cert") == 'themoviedb.org':
                data_release = ''
                errmsg = ''
                try:
                    data_release = tmdb.get_releases(item['imdbnumber'])
                except HTTP404Error, e:
                    errmsg = '404: File not found'
                    data_result = 'skipping'
                except HTTP503Error, e:
                    errmsg = '503: API Limit Exceeded'
                    data_result = 'retrying'
                except ItemNotFoundError, e:
                    errmsg = '%s not found' % item['name']
                    data_result = 'skipping'
                except ExpatError, e:
                    errmsg = 'Error parsing xml: %s' % str(e)
                    data_result = 'retrying'
                except HTTPTimeout, e:
                    errmsg = 'Timed out'
                    data_result = 'skipping'
                except DownloadError, e:
                    errmsg = 'Possible network error: %s' % str(e)
                    data_result = 'skipping'
                else:
                    pass
                if errmsg:
                    log(errmsg)
                if data_release:
                    if data_release['mpaa']:
                        if __addon__.getSetting("movie_cert_nota") == '0':
                            new_mpaa = '"Rated %s"' %data_release['mpaa']
                        elif __addon__.getSetting("movie_cert_nota") == '1':
                            new_mpaa = '"%s_%s"' %(data_release['iso_3166_1'], data_release['mpaa'])
                        else:
                            new_mpaa = '"%s:%s"' %(data_release['iso_3166_1'], data_release['mpaa'])
                        if not item['mpaa'] in new_mpaa:
                            log('new mpaa: %s, old mpaa: %s' %(new_mpaa, item['mpaa']))
                            new_info['mpaa'] = new_mpaa
                            update_media = True
            
            if (__addon__.getSetting(id="movie_cert") or __addon__.getSetting(id="movie_cert")) == 'IMDb':
                movie_data = ''
                errmsg = ''
                try:
                    movie_data = imdb.get_ratings(item['imdbnumber'])
                except HTTP404Error, e:
                    errmsg = '404: File not found'
                    data_result = 'skipping'
                except HTTP503Error, e:
                    errmsg = '503: API Limit Exceeded'
                    data_result = 'retrying'
                except ItemNotFoundError, e:
                    errmsg = '%s not found' % item['name']
                    data_result = 'skipping'
                except ExpatError, e:
                    errmsg = 'Error parsing xml: %s' % str(e)
                    data_result = 'retrying'
                except HTTPTimeout, e:
                    errmsg = 'Timed out'
                    data_result = 'skipping'
                except DownloadError, e:
                    errmsg = 'Possible network error: %s' % str(e)
                    data_result = 'skipping'
                else:
                    pass
                if errmsg:
                    log(errmsg)
                if movie_data:
                    if __addon__.getSetting(id="movie_cert") == 'IMDb' and movie_data['mpaa']:
                        if __addon__.getSetting("movie_cert_nota") == '0':
                            new_mpaa = '"Rated %s"' %movie_data['mpaa']
                        elif __addon__.getSetting("movie_cert_nota") == '1':
                            new_mpaa = '"%s_%s"' %('us', movie_data['mpaa'])
                        else:
                            new_mpaa = '"%s:%s"' %('us', movie_data['mpaa'])
                        if not item['mpaa'] in new_mpaa:
                            log('new mpaa: %s, old mpaa: %s' %(new_mpaa, item['mpaa']))
                            new_info['mpaa'] = new_mpaa
                            update_media = True
                    if __addon__.getSetting(id="movie_rating") == 'IMDb' and movie_data['rating']:
                        if item['votes'] < movie_data['votes']:
                            log('new rating: %s, old rating: %s' %(movie_data['rating'], item['rating']))
                            log('new votes: %s, old votes: %s' %(movie_data['votes'], item['votes']))
                            new_info['rating'] = float(movie_data['rating'])
                            new_info['votes'] = '"%s"' %movie_data['votes']
                            update_media = True

            log('update: %s' %update_media)
            if update_media:
                set_library(item, new_info)
                pass
        processeditems += 1


### Start of script
if (__name__ == '__main__'):
    log('######## Library info update: Initializing...............................', xbmc.LOGNOTICE)
    log('## Add-on ID   = %s' % str(__addonid__), xbmc.LOGNOTICE)
    log('## Add-on Name = %s' % str(__addonname__), xbmc.LOGNOTICE)
    log('## Authors     = %s' % str(__author__), xbmc.LOGNOTICE)
    log('## Version     = %s' % str(__version__), xbmc.LOGNOTICE)
    Main()
    log('## Script stopped or ended', xbmc.LOGNOTICE)