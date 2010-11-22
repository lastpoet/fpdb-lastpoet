#! /usr/bin/env python

__author__ = "Forrest"
__version__ = "0.1"

import logging, os, sys
import re, urllib2
logger = logging.getLogger("winamax_get_winning")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


def winamax_get_winning( tourney_id, hero_name):
    url= "https://www.winamax.fr/poker/tournament.php?ID=%d"%tourney_id
    data = urllib2.urlopen(url).read()
    re_Winning = re.compile(r"""%s</td><td width=\"60.\">(?P<WINNING>\d+(,\d+)?)"""%hero_name)
    m = re_Winning.search(data)
    if m:
        s = m.groupdict().get('WINNING')
        s = s.replace(",",".")
        s = float(s)
        return s
    else:
        return 0.0

def main():
    import optparse
    parser = optparse.OptionParser(
        usage='\n\t%prog [options]',
        version='%%prog %s' % __version__)
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="be verbose")
    (options, args) = parser.parse_args(sys.argv[1:])
    print winamax_get_winning(2052839,"beecool57")
if __name__ == '__main__':
    main()
