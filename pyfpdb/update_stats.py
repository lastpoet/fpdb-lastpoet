#! /usr/bin/env python

__author__ = "Forrest"
__version__ = "0.1"

import logging, sys, os
logger = logging.getLogger("update_stats")
import Database, SQL, Configuration


def main():
    import optparse
    parser = optparse.OptionParser(
        usage='\n\t%prog [options]',
        version='%%prog %s' % __version__)
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="be verbose")
    (options, args) = parser.parse_args(sys.argv[1:])


    config = Configuration.Config(file=".fpdb/HUD_config.xml" , dbname="sqlite")
    sql = SQL.Sql(db_server = 'sqlite')
    db = Database.Database(config,sql)
    cursor = db.cursor
    query = open("stats_query.sql").read()
    cursor.execute("DROP TABLE stats")
    cursor.execute(""" CREATE TABLE IF NOT EXISTS stats (
Name VARCHAR(200),
Name2 VARCHAR(200),
Game_type VARCHAR(200),
Game_var VARCHAR(200),
Lim VARCHAR(200),
Sites VARCHAR(200),
Blind_min INTEGER,
Blind_max INTEGER,
Game_var2 VARCHAR(200),
Hds INTEGER,
VPIP FLOAT,
PFR FLOAT,
PF3 FLOAT,
NA1 FLOAT,
Steals FLOAT,
SawF FLOAT,
SawSD FLOAT,
WtSDwsF FLOAT,
W$SD FLOAT,
FlAFq FLOAT,
TuAFq FLOAT,
RvAFq FLOAT,
NA2 FLOAT,
NA3 FLOAT,
AggFreq FLOAT,
ContBet FLOAT,
Net FLOAT,
Rake FLOAT,
bb100 FLOAT,
NA4 FLOAT,
bbxr100 FLOAT,
NA5 FLOAT,
NA6 FLOAT,
Variance FLOAT
)
"""
                   )
    query = query.replace("\n"," ")
    cursor.execute(query)
    res = cursor.fetchall()
    for line in res:
        cmd = """INSERT INTO stats VALUES %s """%str(line)
        cmd = cmd.replace("u'","'")
        cmd = cmd.replace("None",'0')
#        print line
#        print cmd
        cursor.execute(cmd)
        db.commit()

if __name__ == '__main__':
    main()
