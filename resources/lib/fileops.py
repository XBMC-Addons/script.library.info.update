#import modules
import os
import socket
import urllib2
import urllib
import xbmc
import xbmcvfs

### import libraries
from traceback import print_exc
from urllib2 import HTTPError, URLError
from resources.lib.script_exceptions import *
from resources.lib import utils
from resources.lib.utils import log

THUMBS_CACHE_PATH = xbmc.translatePath( "special://profile/Thumbnails/Video" )


### adjust default timeout to stop script hanging
timeout = 10
socket.setdefaulttimeout(timeout)

class fileops:
    """
    This class handles all types of file operations needed by
    script.extrafanartdownloader (creating directories, downloading
    files, copying files etc.)
    """

    def __init__(self):
        log("Setting up fileops")
        self._exists = lambda path: xbmcvfs.exists(path)
        self._rmdir = lambda path: xbmcvfs.rmdir(path)
        self._mkdir = lambda path: xbmcvfs.mkdir(path)
        self._delete = lambda path: xbmcvfs.delete(path)

        self.downloadcount = 0
        self.tempdir = os.path.join(utils.__addonprofile__, 'temp')
        if not self._exists(self.tempdir):
            if not self._exists(utils.__addonprofile__):
                if not self._mkdir(utils.__addonprofile__):
                    raise CreateDirectoryError(utils.__addonprofile__)
            if not self._mkdir(self.tempdir):
                raise CreateDirectoryError(self.tempdir)
        
    def _copy(self, source, target):
        return xbmcvfs.copy(source.encode("utf-8"), target.encode("utf-8"))

    ### Delete file from all targetdirs
    def _delete_file_in_dirs(self, filename, targetdirs, reason, media_name = '' ):
        isdeleted = False
        for targetdir in targetdirs:
            path = os.path.join(targetdir, filename)
            if self._exists(path):
                self._delete(path)
                log("[%s] Deleted (%s): %s" % (media_name, reason, path))
                isdeleted = True
        if not isdeleted:
            log("[%s] Ignoring (%s): %s" % (media_name, reason, filename))


    # copy file from temp to final location
    def _copyfile(self, sourcepath, targetpath, media_name = ''):
        targetdir = os.path.dirname(targetpath).encode("utf-8")
        if not self._exists(targetdir):
            if not self._mkdir(targetdir):
                raise CreateDirectoryError(targetdir)
        if not self._copy(sourcepath, targetpath):
            raise CopyError(targetpath)
        else:
            log("[%s] Copied successfully: %s" % (media_name, targetpath) )

    # download file
    def _downloadfile(self, url, filename, targetdir, media_name):
        try:
            temppath = os.path.join(self.tempdir, filename)
            tempfile = open(temppath, "wb")
            response = urllib2.urlopen(url)
            tempfile.write(response.read())
            tempfile.close()
            response.close()
        except HTTPError, e:
            if e.code == 404:
                raise HTTP404Error(url)
            else:
                raise DownloadError(str(e))
        except URLError:
            raise HTTPTimeout(url)
        except socket.timeout, e:
            raise HTTPTimeout(url)
        except Exception, e:
            log(str(e), xbmc.LOGNOTICE)
        else:
            log("[%s] Downloaded: %s" % (media_name, filename))
            self.downloadcount += 1
            targetpath = os.path.join(targetdir, filename)
            self._copyfile(temppath, targetpath, media_name)

        
        def cleanup(self):
            if self.fileops._exists(self.fileops.tempdir):
                dialog_msg('update', percentage = 100, line1 = __localize__(32005), background = False)
                log('Cleaning up temp files')
                for x in os.listdir(self.fileops.tempdir):
                    tempfile = os.path.join(self.fileops.tempdir, x)
                    self.fileops._delete(tempfile)
                    if self.fileops._exists(tempfile):
                        log('Error deleting temp file: %s' % tempfile, xbmc.LOGERROR)
                self.fileops._rmdir(self.fileops.tempdir)
                if self.fileops._exists(self.fileops.tempdir):
                    log('Error deleting temp directory: %s' % self.fileops.tempdir, xbmc.LOGERROR)
                else:
                    log('Deleted temp directory: %s' % self.fileops.tempdir)