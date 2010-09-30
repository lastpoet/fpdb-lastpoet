#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright 2008-2010 Ray E. Barker
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU Affero General Public License as published by
#the Free Software Foundation, version 3 of the License.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU Affero General Public License
#along with this program. If not, see <http://www.gnu.org/licenses/>.
#In the "official" distribution you can find the license in agpl-3.0.txt.

import L10n
_ = L10n.get_translation()

import sys
from optparse import OptionParser
#   http://docs.python.org/library/optparse.html

def fpdb_options():

    """Process command line options for fpdb and HUD_main."""
    parser = OptionParser()
    parser.add_option("-x", "--errorsToConsole",
                      action="store_true",
                      help=_("If passed error output will go to the console rather than ."))
    parser.add_option("-d", "--databaseName",
                      dest="dbname",
                      help=_("Overrides the default database name"))
    parser.add_option("-c", "--configFile",
                      dest="config", default=None,
                      help=_("Specifies a configuration file."))
    parser.add_option("-r", "--rerunPython",
                      action="store_true",
                      help=_("Indicates program was restarted with a different path (only allowed once)."))
    parser.add_option("-i", "--infile",
                      dest="infile", default="Slartibartfast",
                      help=_("Input file"))
    parser.add_option("-k", "--konverter",
                      dest="hhc", default="PokerStarsToFpdb",
                      help=_("Module name for Hand History Converter"))
    parser.add_option("-l", "--logging",
                      dest = "log_level", 
                      choices = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'EMPTY'),
                      help = _("Error logging level:")+" (DEBUG, INFO, WARNING, ERROR, CRITICAL, EMPTY)",
                      default = 'EMPTY')
    parser.add_option("-v", "--version", action = "store_true", 
                      help = _("Print version information and exit."))
    parser.add_option("-u", "--usage", action="store_true", dest="usage", default=False,
                    help=_("Print some useful one liners"))


    (options, argv) = parser.parse_args()
    return (options, argv)

if __name__== "__main__":
    (options, argv) = fpdb_options()
    print "errorsToConsole =", options.errorsToConsole
    print "database name   =", options.dbname
    print "config file     =", options.config

    print _("press enter to end")
    sys.stdin.readline()
