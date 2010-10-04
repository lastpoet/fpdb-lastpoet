#! /usr/bin/env python

__author__ = "Forrest"
__version__ = "0.1"

import logging
import time
import fcntl
import os, glob, sys
import signal
import time
import tempfile, pickle, subprocess

logger = logging.getLogger('histwatcher')
try:
    p = os.path.join(os.environ['HOME'],'.fpdb','cache')
    os.makedirs(p)
except OSError:
    logger.info("Path existed %s"%p)


class Watcher(object):
    cached_file = os.path.join(os.environ['HOME'],'.fpdb','cache','hist.pickle')

    def __init__(self, directory, site):
        """

        Arguments:
        - `folername`:
        """
        self._dir = directory
        self.parsed_byte = {}
        self.site = site
        if os.path.isfile(self.cached_file):
            f = open(self.cached_file)
            self.cached = pickle.load(f)
            f.close()
        else:
            self.cached = {}
        if not self.cached.get(site):
            self.cached[site] = []

        self.flist = self.cached.get(site) # flist [ (file,last_read,byte_read,isNew) ]

    def update_flist(self):
        existing_files = glob.glob(os.path.join(self._dir,'*'))
        self.cached_files = [ f[0] for f in self.flist ]
        for f in existing_files:
            full_path = os.path.join(self._dir, f)
            if not os.path.isfile(full_path):
                continue

            if not full_path in self.cached_files:
                self.flist.append([full_path,0,0,True]) ## new file -> readtime = 0 ; byte_read = 0

        for i in range(len(self.flist)):
            self.flist[i][3] = False
            f = self.flist[i]
            full_path = f[0]
            last_read = f[1]

            mtime = os.stat(full_path).st_mtime

            if mtime > last_read:
                self.flist[i][3] = True

    def parse_hist(self):
        for i in range(len(self.flist)):
            f = self.flist[i]
            if f[3] == False: # the file is not new
                continue

            filename = f[0]
            fh = open(filename)
            byte_read = f[2]
            fh.seek(byte_read)
            print "Parsing recently modified file %s"%filename
            new_lines = fh.read()

            tempf = tempfile.NamedTemporaryFile(delete=False)
            tempf.write(new_lines)
            # print tempf.name
            logf = open(os.path.join(os.environ['HOME'],'.fpdb','log','histwatcher.log'),'a')
            subprocess.call("./GuiBulkImport.py -c %s -f %s"
                            %(self.site, tempf.name), shell = True, stdout = logf, stderr = logf)
            logf.close()
            os.devnull
            #print "./GuiBulkImport.py -c %s -f %s "%(self.site, tempf.name)
            tempf.close()
            os.unlink(tempf.name)
            self.flist[i] = ([filename,time.time(),fh.tell(),False])

    def run(self):
        """

        Arguments:
        - `self`:
        """
        cnt = 0
        while [ 1 ]:
            self.parse_hist()
            time.sleep(0.1)
            cnt +=1
            if cnt % 10:
                self.update_flist()
                f = open(self.cached_file,'w')
                pickle.dump(self.cached,f)
                f.close()

def main():
    import optparse
    parser = optparse.OptionParser(
        usage='\n\t%prog [options] folder',
        version='%%prog %s' % __version__)
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="be verbose")

    parser.add_option("-s", "--site",
                      dest="site", default="Winamax",
                      help="site name")

    (options, args) = parser.parse_args(sys.argv[1:])

    if len(args) != 1:
        parser.error('%prog [options] folder')
        return

    directory = args[0]
    watcher = Watcher(directory,options.site)
    watcher.run()

if __name__ == '__main__':
    main()
