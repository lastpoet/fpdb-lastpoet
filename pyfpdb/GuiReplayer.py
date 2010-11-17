#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Copyright 2010 Maxime Grandchamp
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


from Hand import *
import Configuration
import Database
import SQL
import fpdb_import
import Filters
import pygtk
pygtk.require('2.0')
import gtk
import math
from time import sleep

MyStack={}

class GuiReplayer:
    def __init__(self, config, querylist, mainwin, debug=True):
        self.debug = debug
        self.conf = config
        self.main_window = mainwin
        self.sql = querylist
        
        self.db = Database.Database(self.conf, sql=self.sql)
        
        filters_display = { "Heroes"    : True,
                    "Sites"     : True,
                    "Games"     : True,
                    "Limits"    : True,
                    "LimitSep"  : True,
                    "LimitType" : True,
                    "Type"      : True,
                    "Seats"     : True,
                    "SeatSep"   : True,
                    "Dates"     : True,
                    "Groups"    : True,
                    "GroupsAll" : True,
                    "Button1"   : True,
                    "Button2"   : True
                  }
        
        
        self.filters = Filters.Filters(self.db, self.conf, self.sql, display = filters_display)
        #self.filters.registerButton1Name(_("Import Hand"))
        #self.filters.registerButton1Callback(self.importhand)
        #self.filters.registerButton2Name(_("temp"))
        #self.filters.registerButton2Callback(self.temp())

        # hierarchy:  self.mainHBox / self.hpane / self.replayBox / self.area 

        self.mainHBox = gtk.HBox(False, 0)
        self.mainHBox.show()

        self.leftPanelBox = self.filters.get_vbox()

        self.hpane = gtk.HPaned()
        self.hpane.pack1(self.leftPanelBox)
        self.mainHBox.add(self.hpane)

        self.replayBox = gtk.VBox(False, 0)
        self.replayBox.show()
        
        self.hpane.pack2(self.replayBox)
        self.hpane.show()

        self.area=gtk.DrawingArea()
        self.pangolayout = self.area.create_pango_layout("")        
        self.area.connect("expose-event", self.area_expose)
        self.style = self.area.get_style()
        self.gc = self.style.fg_gc[gtk.STATE_NORMAL]      
        self.area.show()

        self.replayBox.pack_start(self.area)



                   

    def launch_play(self):
        MyHand = self.importhand()
        if isinstance(MyHand, HoldemOmahaHand):
            if MyHand.gametype['category'] == 'holdem':
                self.play_holdem(MyHand)

       
                    
    def area_expose(self, area, event):
        global ready
        self.style = self.area.get_style()
        self.gc = self.style.fg_gc[gtk.STATE_NORMAL]
        print "expose"
        self.launch_play()       


    def play_holdem(self,MyHand):
        maxseats=MyHand.maxseats
        pos={}

        self.area.window.draw_arc(self.gc, 0, 125, 125, 300, 300, 0, 360*64) #table

        #setup the table with names and initial stacks
        for i in range(0,maxseats):     # radius: 200, center: 250,250
            x= int (round(250+200*math.cos(2*i*math.pi/maxseats)))
            y= int (round(250+200*math.sin(2*i*math.pi/maxseats)))            
            try:
                pos[MyHand.players[i][1]]=(x,y)               #save coordinates of each player            
                self.pangolayout.set_text(MyHand.players[i][1])     #player names 
                self.area.window.draw_layout(self.gc, x, y, self.pangolayout)                                 
                self.pangolayout.set_text('$'+MyHand.players[i][2])     #player stacks
                self.area.window.draw_layout(self.gc, x+10, y+20, self.pangolayout)
                MyStack[MyHand.players[i][1]]=Decimal(MyHand.players[i][2]) #saves stack
            except IndexError:  #if seat is empty
                pass 
              
        cm = self.gc.get_colormap()
        color = cm.alloc_color("red")                      
        self.gc.set_foreground(color)

        
        print MyStack
        
        self.draw_actions('BLINDSANTES', MyHand, pos)        
        self.draw_actions('PREFLOP', MyHand, pos)
        self.draw_actions('FLOP', MyHand, pos)
        self.draw_actions('TURN', MyHand, pos)
        self.draw_actions('RIVER', MyHand, pos)
                     
        color = cm.alloc_color("black")                      
        self.gc.set_foreground(color)
        
        print MyStack
        

    def draw_action(self, pos, i):
        self.pangolayout.set_text(i[1]) #displays action
    #gets text size
    #            text_width, text_height = self.pangolayout.get_pixel_size()
    #            print text_width, text_height
    #max seen  72 17
    #clear area
        cm = self.gc.get_colormap()
        color = cm.alloc_color("lightgrey")
        self.gc.set_foreground(color)
        self.area.window.draw_rectangle(self.gc, True, pos[i[0]][0] + 10, pos[i[0]][1] + 35, 80, 20)
        color = cm.alloc_color("red")
        self.gc.set_foreground(color)
        self.area.window.draw_layout(self.gc, pos[i[0]][0] + 10, pos[i[0]][1] + 35, self.pangolayout)
        try:
            self.pangolayout.set_text(str(i[2])) #displays amount
            self.area.window.draw_layout(self.gc, pos[i[0]][0] + 10, pos[i[0]][1] + 55, self.pangolayout)
            MyStack[i[0]] -= i[2]
        except:
            #no amount
            pass
        rect = gtk.gdk.Rectangle(pos[i[0]][0] + 10, pos[i[0]][1] + 35, 80, 20)
        self.area.window.invalidate_rect(rect, False)
        self.area.window.process_updates(False)
        print "redraw"


    def draw_actions(self, action, MyHand, pos):
        for i in MyHand.actions[action]:            
            self.draw_action(pos, i)



    def get_vbox(self):
        """returns the vbox of this thread"""
        return self.mainHBox

    def importhand(self, handnumber=1):
        """Temporary function that grabs a Hand object from a specified file. Obviously this will
        be replaced by a function to select a hand from the db in the not so distant future.
        This code has been shamelessly stolen from Carl
        """
        config = Configuration.Config(file = "HUD_config.test.xml")
        db = Database.Database(config)
        sql = SQL.Sql(db_server = 'sqlite')
        settings = {}
        settings.update(config.get_db_parameters())
        settings.update(config.get_import_parameters())
        settings.update(config.get_default_paths())
        #db.recreate_tables()
        importer = fpdb_import.Importer(False, settings, config, None)
        importer.setDropIndexes("don't drop")
        importer.setFailOnError(True)
        importer.setThreads(-1)
        importer.setCallHud(False)
        importer.setFakeCacheHHC(True)
        
        #Get a simple regression file with a few hands of Hold'em
        filename="regression-test-files/cash/Stars/Flop/NLHE-FR-USD-0.01-0.02-201005.microgrind.txt"
        site="PokerStars"
        
        
        importer.addBulkImportImportFileOrDir(filename, site=site)
        (stored, dups, partial, errs, ttime) = importer.runImport()
        
                        
        hhc = importer.getCachedHHC()
        handlist = hhc.getProcessedHands()        
 
        return handlist[0]
       
            
    def temp(self):
        pass

