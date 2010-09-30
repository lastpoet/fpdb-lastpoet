#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright 2008-2010, Carl Gherardi
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
########################################################################


import L10n
_ = L10n.get_translation()

import sys
import exceptions

import logging
# logging has been set up in fpdb.py or HUD_main.py, use their settings:

import Configuration
from HandHistoryConverter import *
from decimal import Decimal
import time

# Winamax HH Format

class Winamax(HandHistoryConverter):
    def Trace(f):
        def my_f(*args, **kwds):
            print ( "entering " +  f.__name__)
            result= f(*args, **kwds)
            print ( "exiting " +  f.__name__)
            return result
        my_f.__name = f.__name__
        my_f.__doc__ = f.__doc__
        return my_f

    filter = "Winamax"
    siteName = "Winamax"
    filetype = "text"
    codepage = ("utf8", "cp1252")
    siteId   = 14 # Needs to match id entry in Sites database

    mixes = { } # Legal mixed games
    sym = {'USD': "\$", 'CAD': "\$", 'T$': "", "EUR": "\xe2\x82\xac", "GBP": "\xa3"}         # ADD Euro, Sterling, etc HERE
    substitutions = {
                     'LEGAL_ISO' : "USD|EUR|GBP|CAD|FPP",    # legal ISO currency codes
                            'LS' : "\$|\xe2\x82\xac|"        # legal currency symbols - Euro(cp1252, utf-8)
                    }

    limits = { 'no limit':'nl', 'pot limit' : 'pl','LIMIT':'fl'}

    games = {                          # base, category
                                "Holdem" : ('hold','holdem'),
                                 'Omaha' : ('hold','omahahi'),
             #             'Omaha Hi/Lo' : ('hold','omahahilo'),
             #                    'Razz' : ('stud','razz'),
             #                    'RAZZ' : ('stud','razz'),
             #             '7 Card Stud' : ('stud','studhi'),
                 'SEVEN_CARD_STUD_HI_LO' : ('stud','studhilo'),
             #                  'Badugi' : ('draw','badugi'),
             # 'Triple Draw 2-7 Lowball' : ('draw','27_3draw'),
             #             '5 Card Draw' : ('draw','fivedraw')
               }

    # Static regexes
    # ***** End of hand R5-75443872-57 *****
    re_SplitHands = re.compile(r'\n\n')



# Winamax Poker - CashGame - HandId: #279823-223-1285031451 - Holdem no limit (0.02€/0.05€) - 2010/09/21 03:10:51 UTC
# Table: 'Charenton-le-Pont' 9-max (real money) Seat #5 is the button

    re_HandInfo = re.compile(u"""
            \s*Winamax\sPoker\s-\sCashGame\s-\sHandId:\s\#(?P<HID1>\d+)-(?P<HID2>\d+)-(?P<HID3>\d+).*\s
            (?P<GAME>Holdem|Omaha)\s
            (?P<LIMIT>no\slimit|pot\slimit)\s
            \(
            ((%(LS)s)?(?P<SB>[.0-9]+)(%(LS)s)?)/
            ((%(LS)s)?(?P<BB>[.0-9]+)(%(LS)s)?)
            \)\s-\s
            (?P<DATETIME>.*)
            Table:\s\'(?P<TABLE>[^']+)\'\s(?P<MAXPLAYER>\d+)\-max
            """ % substitutions, re.MULTILINE|re.DOTALL|re.VERBOSE)

    re_TailSplitHands = re.compile(r'\n\s*\n')
    re_Button       = re.compile(r'Seat\s#(?P<BUTTON>\d+)\sis\sthe\sbutton')
    re_Board        = re.compile(r"\[(?P<CARDS>.+)\]")

    # 2010/09/21 03:10:51 UTC
    re_DateTime = re.compile("""
            (?P<Y>[0-9]{4})/
            (?P<M>[0-9]+)/
            (?P<D>[0-9]+)\s
            (?P<H>[0-9]+):(?P<MIN>[0-9]+):(?P<S>[0-9]+)\s
            UTC
            """, re.MULTILINE|re.VERBOSE)

# Seat 1: some_player (5€)
# Seat 2: some_other_player21 (6.33€)

    re_PlayerInfo = re.compile(u'Seat\s(?P<SEAT>[0-9]+):\s(?P<PNAME>.*)\s\((%(LS)s)?(?P<CASH>[.0-9]+)(%(LS)s)?\)' % substitutions)

    def compilePlayerRegexs(self, hand):
        players = set([player[1] for player in hand.players])
        if not players <= self.compiledPlayers: # x <= y means 'x is subset of y'
            # we need to recompile the player regexs.
# TODO: should probably rename re_HeroCards and corresponding method,
#    since they are used to find all cards on lines starting with "Dealt to:"
#    They still identify the hero.
            self.compiledPlayers = players
            #ANTES/BLINDS
            #helander2222 posts blind ($0.25), lopllopl posts blind ($0.50).
            player_re = "(?P<PNAME>" + "|".join(map(re.escape, players)) + ")"
            subst = {'PLYR': player_re, 'CUR': self.sym[hand.gametype['currency']]}
            self.re_PostSB    = re.compile('%(PLYR)s posts small blind (%(CUR)s)?(?P<SB>[\.0-9]+)(%(CUR)s)?' % subst, re.MULTILINE)
            self.re_PostBB    = re.compile('%(PLYR)s posts big blind (%(CUR)s)?(?P<BB>[\.0-9]+)(%(CUR)s)?' % subst, re.MULTILINE)
            self.re_DenySB    = re.compile('(?P<PNAME>.*) deny SB' % subst, re.MULTILINE)
            self.re_Antes     = re.compile(r"^%(PLYR)s: posts the ante (%(CUR)s)?(?P<ANTE>[\.0-9]+)(%(CUR)s)?" % subst, re.MULTILINE)
            self.re_BringIn   = re.compile(r"^%(PLYR)s: brings[- ]in( low|) for (%(CUR)s)?(?P<BRINGIN>[\.0-9]+(%(CUR)s)?)" % subst, re.MULTILINE)
            self.re_PostBoth  = re.compile('(?P<PNAME>.*): posts small \& big blind \( (%(CUR)s)?(?P<SBBB>[\.0-9]+)(%(CUR)s)?\)' % subst)
            self.re_PostDead  = re.compile('(?P<PNAME>.*) posts dead blind \((%(CUR)s)?(?P<DEAD>[\.0-9]+)(%(CUR)s)?\)' % subst, re.MULTILINE)
            self.re_HeroCards = re.compile('Dealt\sto\s%(PLYR)s\s\[(?P<CARDS>.*)\]' % subst)

            self.re_Action = re.compile('(, )?(?P<PNAME>.*?)(?P<ATYPE> bets| checks| raises| calls| folds)( (%(CUR)s)?(?P<BET>[\d\.]+)(%(CUR)s)?)?( and is all-in)?' % subst)
            self.re_ShowdownAction = re.compile('(?P<PNAME>[^\(\)\n]*) (\((small blind|big blind|button)\) )?shows \[(?P<CARDS>.+)\]')
            self.re_CollectPot = re.compile('\s*(?P<PNAME>.*)\scollected\s(%(CUR)s)?(?P<POT>[\.\d]+)(%(CUR)s)?.*' % subst)
            self.re_ShownCards = re.compile("^Seat (?P<SEAT>[0-9]+): %(PLYR)s showed \[(?P<CARDS>.*)\].*" % subst, re.MULTILINE)
            self.re_sitsOut    = re.compile('(?P<PNAME>.*) sits out')

    def readSupportedGames(self):
        return [
                ["ring", "hold", "fl"],
                ["ring", "hold", "nl"],
                ["ring", "hold", "pl"],
                ["ring", "stud", "fl"],
               ]

    def determineGameType(self, handText):
        # Inspect the handText and return the gametype dict
        # gametype dict is: {'limitType': xxx, 'base': xxx, 'category': xxx}
        info = {}

        m = self.re_HandInfo.search(handText)
        if not m:
            tmp = handText[0:100]
            log.error(_("determineGameType: Unable to recognise gametype from: '%s'") % tmp)
            log.error(_("determineGameType: Raising FpdbParseError"))
            raise FpdbParseError(_("Unable to recognise gametype from: '%s'") % tmp)

        mg = m.groupdict()

        info['type'] = 'ring'
        info['currency'] = 'EUR'

        if 'LIMIT' in mg:
            if mg['LIMIT'] in self.limits:
                info['limitType'] = self.limits[mg['LIMIT']]
            else:
                tmp = handText[0:100]
                log.error(_("determineGameType: limit not found in self.limits(%s). hand: '%s'") % (str(mg),tmp))
                log.error(_("determineGameType: Raising FpdbParseError"))
                raise FpdbParseError(_("limit not found in self.limits(%s). hand: '%s'") % (str(mg),tmp))
        if 'GAME' in mg:
            (info['base'], info['category']) = self.games[mg['GAME']]
        if 'SB' in mg:
            info['sb'] = mg['SB']
        if 'BB' in mg:
            info['bb'] = mg['BB']

        return info

    def readHandInfo(self, hand):
        info = {}
        m =  self.re_HandInfo.search(hand.handText)

        if m:
            info.update(m.groupdict())

        #self.log.debug("readHandInfo: %s" % info)
        for key in info:
            if key == 'DATETIME':
                a = self.re_DateTime.search(info[key])
                if a:
                    datetimestr = "%s/%s/%s %s:%s:%s" % (a.group('Y'),a.group('M'), a.group('D'), a.group('H'),a.group('MIN'),a.group('S'))
                    tzoffset = str(-time.timezone/3600)
                else:
                    datetimestr = "2010/Jan/01 01:01:01"
                    log.error(_("readHandInfo: DATETIME not matched: '%s'" % info[key]))
                    print "DEBUG: readHandInfo: DATETIME not matched: '%s'" % info[key]
                # TODO: Manually adjust time against OFFSET
                hand.startTime = datetime.datetime.strptime(datetimestr, "%Y/%m/%d %H:%M:%S") # also timezone at end, e.g. " ET"
                hand.startTime = HandHistoryConverter.changeTimezone(hand.startTime, "CET", "UTC")
            if key == 'HID1':
                hand.handid = "1%.4d%s%s"%(int(info['HID2']),info['HID1'],info['HID3'])
                # Need to remove non-alphanumerics for MySQL
            if key == 'TABLE':
                hand.tablename = info[key]

        # TODO: These
        hand.buttonpos = 1
        hand.maxseats = 10    # Set to None - Hand.py will guessMaxSeats()
        hand.mixed = None

    def readPlayerStacks(self, hand):
        log.info("readplayerstacks: re is '%s'" % self.re_PlayerInfo)
        m = self.re_PlayerInfo.finditer(hand.handText)
        for a in m:
            print "DEBUG: found '%s' with '%s'" %(a.group('PNAME'), a.group('CASH'))
            hand.addPlayer(int(a.group('SEAT')), a.group('PNAME'), a.group('CASH'))


    def markStreets(self, hand):
# *** ANTE/BLINDS ***
# Player1 posts small blind 0.02€
# Player2 posts big blind 0.05€
# Dealt to Player6 [5d Kh 9c Tc]
# *** PRE-FLOP ***
# Player3 folds
# Player4 calls 0.05€
# Player5 folds
# Player6 calls 0.05€
# Player8 calls 0.05€
# Player9 folds
# Player1 calls 0.03€
# Player2 checks
# *** FLOP *** [5h 8d 3h]
# Player1 checks
# Player2 checks
# Player7 checks
# Player6 checks
# Player8 checks
# *** TURN *** [5h 8d 3h][7h]
# Player1 checks
# Player2 checks
# Player7 checks
# Player6 checks
# Player8 checks
# *** RIVER *** [5h 8d 3h 7h][2d]
# Player1 checks
# Player2 checks
# Player7 checks
# Player6 bets 0.25€
# Player8 folds
# Player1 folds
# Player2 folds
# Player7 calls 0.25€
# *** SHOW DOWN ***
# Player6 shows [5d Kh 9c Tc] (One pair : 5)
# Player7 shows [6h Js 9s Td] (Straight 9 high)
# Player7 collected 0.71€ from pot
# *** SUMMARY ***
# Total pot 0.71€ | Rake 0.04€

        m =  re.search(r"\*\*\* ANTE/BLINDS \*\*\*(?P<BLINDSANTES>.+(?=\*\*\* PRE-FLOP \*\*\*)|.+(?=\*\*\* SUMMARY \*\*\*))"
                       r"\*\*\* PRE-FLOP \*\*\*(?P<PREFLOP>.+(?=\*\*\* FLOP \*\*\*)|.+(?=\*\*\* SUMMARY \*\*\*))"
                       r"( *\*\*\* FLOP \*\*\* (?P<FLOP>\[\w\w \w\w \w\w\].+(?=\*\*\* TURN \*\*\*)|.+(?=\*\*\* SUMMARY \*\*\*)))?"
                       r"( *\*\*\* TURN \*\*\* \[\w\w \w\w \w\w\](?P<TURN>\[\w\w\].+(?=\*\*\* RIVER \*\*\*)|.+(?=\*\*\*\SUMMARY \*\*\*)))?"
                       r"( *\*\*\* RIVER \*\*\* \[\w\w \w\w \w\w \w\w\](?P<RIVER>\[\w\w\].+(?=\*\*\* SUMMARY \*\*\*)))?", hand.handText, re.DOTALL)
        try:
            hand.addStreets(m)
        except:
            print ("Failed to add streets. handtext=%s")

    #Needs to return a list in the format
    # ['player1name', 'player2name', ...] where player1name is the sb and player2name is bb,
    # addtional players are assumed to post a bb oop

    def readButton(self, hand):
        m = self.re_Button.search(hand.handText)
        if m:
            hand.buttonpos = int(m.group('BUTTON'))
            log.debug('readButton: button on pos %d'%hand.buttonpos)
        else:
            log.warning(_('readButton: not found'))

#    def readCommunityCards(self, hand, street):
#        #print hand.streets.group(street)
#        if street in ('FLOP','TURN','RIVER'):   # a list of streets which get dealt community cards (i.e. all but PREFLOP)
#            m = self.re_Board.search(hand.streets.group(street))
#            hand.setCommunityCards(street, m.group('CARDS').split(','))

    def readCommunityCards(self, hand, street): # street has been matched by markStreets, so exists in this hand
        if street in ('FLOP','TURN','RIVER'):   # a list of streets which get dealt community cards (i.e. all but PREFLOP)
            #print "DEBUG readCommunityCards:", street, hand.streets.group(street)
            m = self.re_Board.search(hand.streets[street])
            hand.setCommunityCards(street, m.group('CARDS').split(' '))

    def readBlinds(self, hand):
        if not self.re_DenySB.search(hand.handText):
            try:
                m = self.re_PostSB.search(hand.handText)
                hand.addBlind(m.group('PNAME'), 'small blind', m.group('SB'))
            except exceptions.AttributeError: # no small blind
                self.log.warning( _("readBlinds in noSB exception - no SB created")+str(sys.exc_info()) )
            #hand.addBlind(None, None, None)
        for a in self.re_PostBB.finditer(hand.handText):
            hand.addBlind(a.group('PNAME'), 'big blind', a.group('BB'))
        for a in self.re_PostDead.finditer(hand.handText):
            #print "DEBUG: Found dead blind: addBlind(%s, 'secondsb', %s)" %(a.group('PNAME'), a.group('DEAD'))
            hand.addBlind(a.group('PNAME'), 'secondsb', a.group('DEAD'))
        for a in self.re_PostBoth.finditer(hand.handText):
            hand.addBlind(a.group('PNAME'), 'small & big blinds', a.group('SBBB'))

    def readAntes(self, hand):
        log.debug(_("reading antes"))
        m = self.re_Antes.finditer(hand.handText)
        for player in m:
            #~ logging.debug("hand.addAnte(%s,%s)" %(player.group('PNAME'), player.group('ANTE')))
            hand.addAnte(player.group('PNAME'), player.group('ANTE'))

    def readBringIn(self, hand):
        m = self.re_BringIn.search(hand.handText,re.DOTALL)
        if m:
            #~ logging.debug("readBringIn: %s for %s" %(m.group('PNAME'),  m.group('BRINGIN')))
            hand.addBringIn(m.group('PNAME'),  m.group('BRINGIN'))

    def readHeroCards(self, hand):
        # streets PREFLOP, PREDRAW, and THIRD are special cases beacause
        # we need to grab hero's cards
        for street in ('PREFLOP', 'DEAL', 'BLINDSANTES'):
            if street in hand.streets.keys():
                m = self.re_HeroCards.finditer(hand.streets[street])
            if m == []:
                log.debug("No hole cards found for %s"%street)
            for found in m:
                hand.hero = found.group('PNAME')
                newcards = found.group('CARDS').split(' ')
                print "DEBUG: addHoleCards(%s, %s, %s)" %(street, hand.hero, newcards)
                hand.addHoleCards(street, hand.hero, closed=newcards, shown=False, mucked=False, dealt=True)
                log.debug("Hero cards  %s: %s"%(hand.hero, newcards))

    def readAction(self, hand, street):
        m = self.re_Action.finditer(hand.streets[street])
        for action in m:
            acts = action.groupdict()
            if action.group('ATYPE') == ' raises':
                hand.addRaiseBy( street, action.group('PNAME'), action.group('BET') )
            elif action.group('ATYPE') == ' calls':
                hand.addCall( street, action.group('PNAME'), action.group('BET') )
            elif action.group('ATYPE') == ' bets':
                hand.addBet( street, action.group('PNAME'), action.group('BET') )
            elif action.group('ATYPE') == ' folds':
                hand.addFold( street, action.group('PNAME'))
            elif action.group('ATYPE') == ' checks':
                hand.addCheck( street, action.group('PNAME'))
            elif action.group('ATYPE') == ' discards':
                hand.addDiscard(street, action.group('PNAME'), action.group('BET'), action.group('DISCARDED'))
            elif action.group('ATYPE') == ' stands pat':
                hand.addStandsPat( street, action.group('PNAME'))
            else:
                log.fatal("DEBUG: unimplemented readAction: '%s' '%s'") %(action.group('PNAME'),action.group('ATYPE'),)

    def readShowdownActions(self, hand):
        for shows in self.re_ShowdownAction.finditer(hand.handText):
            log.debug("add show actions %s"%shows)
            cards = shows.group('CARDS')
            cards = cards.split(' ')
            print "DEBUG: addShownCards(%s, %s)" %(cards, shows.group('PNAME'))
            hand.addShownCards(cards, shows.group('PNAME'))

    def readCollectPot(self,hand):
        for m in self.re_CollectPot.finditer(hand.handText):
            hand.addCollectPot(player=m.group('PNAME'),pot=m.group('POT'))


    def readShownCards(self,hand):
        for m in self.re_ShownCards.finditer(hand.handText):
            log.debug("Read shown cards: %s"%m.group(0))
            cards = m.group('CARDS')
            cards = cards.split(' ') # needs to be a list, not a set--stud needs the order
            (shown, mucked) = (False, False)
            if m.group('CARDS') is not None:
                shown = True
                hand.addShownCards(cards=cards, player=m.group('PNAME'), shown=shown, mucked=mucked)

if __name__ == "__main__":
    c = Configuration.Config()
    if len(sys.argv) ==  1:
        testfile = "regression-test-files/ongame/nlhe/ong NLH handhq_0.txt"
    else:
        testfile = sys.argv[1]
    e = Winamax(c, testfile)
