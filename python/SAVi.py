#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# LOCAL MODULES
from classes import *

# GENERAL MODULES
import os
import sys
import wx
import multiprocessing
import datetime
import subprocess
import sqlite3

class MainSAVi(wx.Frame) :
    """This is a frame inherited object setting up the main frame of SAVi"""
    def __init__(self, parent, title) :
        """Class builder"""
        """
        The super function is versatile:
        1. super() is called on a class to get a single inheritance to refer to the parent class without naming it
        In the above case, it is a shortcut
        2. Called in a dynamic environment for multiple inheritance
        USAGE:
        super().methoName(args) #In python 3
        Formerly in py2:
        super(SubClass, self).method(args) #It is still valid in python3
        """

        super().__init__(parent, title=title, size=(1400,800))

        self.Centre()

        self.currentMode = None         # 0 = None LOADED, 1 = PAF LOADED, 2 = DB LOADED
        self.currentPAF = None          # current PAF file
        self.currentDB = None           # current SARead DATABASE
        self.GENEMARKS_FOUND = False    # Sets a GENEMARKS found bool
        self.ALIGNED_FOUND = False      # Sets a ALIGNED found bool

        self.font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.consoleFont = wx.SystemSettings.GetFont(wx.SYS_ANSI_FIXED_FONT)
        self.SetFont(self.font)         # Sets a font for SAVi
        self.init_UI()                  # Inits the GUI

    """
       _____ _    _ _____
      / ____| |  | |_   _|
     | |  __| |  | | | |
     | | |_ | |  | | | |
     | |__| | |__| |_| |_
      \_____|\____/|_____|
    """####################

    def init_UI(self) :
        """Inits menubar and other widgets
          ______ _ _
         |  ____(_) |
         | |__   _| | ___   _ __ ___   ___ _ __  _   _
         |  __| | | |/ _ \ | '_ ` _ \ / _ \ '_ \| | | |
         | |    | | |  __/ | | | | | |  __/ | | | |_| |
         |_|    |_|_|\___| |_| |_| |_|\___|_| |_|\__,_|
        """############################################

        menubar = wx.MenuBar()                                                      # Sets up top menubar
        self.fileMenu = wx.Menu()                                                   # Sets the file menu
        self.fileOpen = self.fileMenu.Append(wx.ID_OPEN, '&Open', 'Open a file')    # Sets the open choice
        self.impgffID = wx.NewId()                                                  # Create an ID for gff importing
        self.importGFF = self.fileMenu.Append(self.impgffID, '&Import GFF',         # Create an import gff choice
        'Import a matching GFF file')
        self.importGFF.Enable(False)                                                # Sets the import gff to Disabled
        self.fileMenu.AppendSeparator()                                             # Separation line
        self.reset_ID = wx.NewId()
        self.closeAndReset = self.fileMenu.Append(self.reset_ID, '&Reset SAVi', 'Closes current files and resets SAVi')
        self.fileMenu.AppendSeparator()
        fileExit = self.fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        helpMenu = wx.Menu()                                                        # Sets up the help menu on top menubar
        helpHelp = helpMenu.Append(wx.ID_HELP, 'Help', 'Miscellaneous')
        helpMenu.AppendSeparator()
        helpAbout = helpMenu.Append(wx.ID_ABOUT, 'About', 'Credits')
        menubar.Append(self.fileMenu, '&File')
        menubar.Append(helpMenu, '&Help')
        self.SetMenuBar(menubar)                                                    # Sets the menubar


        self.layout = wx.BoxSizer(wx.VERTICAL)                                      # Sets a vbox for the mainframe
        self.SetSizer(self.layout)                                                  # Sets self.layout as sizer

        """
          _______          _ _
         |__   __|        | | |
            | | ___   ___ | | |__   __ _ _ __
            | |/ _ \ / _ \| | '_ \ / _` | '__|
            | | (_) | (_) | | |_) | (_| | |
            |_|\___/ \___/|_|_.__/ \__,_|_|
        """###################################

        self.toolbar = wx.ToolBar(self)
        self.toolbar.AddTool(wx.ID_OPEN, 'Open', self.scaleBmp(wx.Bitmap('rsc/open.png'), 50, 50))
        self.toolbar.AddTool(self.impgffID, 'Import GFF', self.scaleBmp(wx.Bitmap('rsc/impGFF.png'), 50, 50))
        self.toolbar.EnableTool(self.impgffID, False) # Disable it while nothing is opened
        self.toolbar.AddSeparator()
        self.toolbar.AddTool(self.reset_ID, 'Close and reset', self.scaleBmp(wx.Bitmap('rsc/close-and-reset.png'), 50, 50))
        self.toolbar.AddSeparator()
        self.toolbar.AddTool(wx.ID_EXIT, 'Exit', self.scaleBmp(wx.Bitmap('rsc/exit.png'), 50, 50))
        self.toolbar.Realize()
        self.layout.Add(self.toolbar, 0, wx.EXPAND)

        """
          _                             _      _____      _     _
         | |                           | |    / ____|    (_)   | |
         | |     __ _ _   _  ___  _   _| |_  | |  __ _ __ _  __| |
         | |    / _` | | | |/ _ \| | | | __| | | |_ | '__| |/ _` |
         | |___| (_| | |_| | (_) | |_| | |_  | |__| | |  | | (_| |
         |______\__,_|\__, |\___/ \__,_|\__|  \_____|_|  |_|\__,_|
                       __/ |
                      |___/
        """#######################################################

        self.HGrid = wx.BoxSizer(wx.HORIZONTAL)
        self.layout.Add(self.HGrid, flag=wx.EXPAND|wx.ALL, proportion=1)
        # Sets a first vertical box (leftmost in HGrid)
        self.VBoxLeft = wx.BoxSizer(wx.VERTICAL)
        self.HGrid.Insert(0, self.VBoxLeft, proportion=2, flag=wx.EXPAND|wx.NORTH|wx.EAST|wx.WEST)
        # Sets a second vertical box (rightmost in HGrid)
        self.VBoxRight = wx.BoxSizer(wx.VERTICAL)
        self.HGrid.Insert(1, self.VBoxRight, proportion=5, flag=wx.EXPAND|wx.ALL)

        """
           __      ______            _           __ _
           \ \    / /  _ \          | |         / _| |
            \ \  / /| |_) | _____  _| |     ___| |_| |_
             \ \/ / |  _ < / _ \ \/ / |    / _ \  _| __|
              \  /  | |_) | (_) >  <| |___|  __/ | | |_
               \/   |____/ \___/_/\_\______\___|_|  \__|
        """##############################################
        # Sets the FIRST frame
        # TEXT
        self.txtOpenButton = wx.StaticText(self, label="1. Open a SARead DB or a .paf file", style=wx.ALIGN_LEFT)
        # LINE
        line = wx.StaticLine(self, wx.HORIZONTAL)
        # BUTTONS
        self.openButton = wx.Button(self, label="Open", size=(100,30))
        self.Bind(wx.EVT_BUTTON, self._open, self.openButton)
        # LAYOUT
        self.VBoxLeft.Add(self.txtOpenButton, flag=wx.EAST, border=2)
        self.VBoxLeft.Add((-1,5), flag=wx.EXPAND)
        self.VBoxLeft.Add(self.openButton, flag=wx.EXPAND)
        self.VBoxLeft.Add((-1,15), flag=wx.EXPAND)
        self.VBoxLeft.Add(line, flag=wx.EXPAND|wx.EAST|wx.WEST)

        # Sets the SECOND frame
        # TEXT
        self.txtRead = wx.StaticText(self, label="2. Read a .paf file (SARead module)", style=wx.ALIGN_LEFT)

        # LINE
        line = wx.StaticLine(self, wx.HORIZONTAL)

        # BUTTONS
        self.readID = wx.NewId()
        self.readButton = wx.Button(self, id=self.readID, label="Read " + str(self.currentPAF))
        self.Bind(wx.EVT_BUTTON, self._read, self.readButton)
        self.readButton.Enable(False)

        self.gffButton = wx.Button(self, id=self.impgffID, label="Import GFF")
        self.Bind(wx.EVT_BUTTON, self._import_gff, self.gffButton)
        self.gffButton.Enable(False)

        # HORIZONTAL SUBLAYOUTS
        self.HSubSecond = wx.BoxSizer(wx.HORIZONTAL)

        # LAYOUT
        self.VBoxLeft.Add(self.txtRead, flag=wx.EAST, border=2)
        self.VBoxLeft.Add((-1,5), flag=wx.EXPAND)
        self.VBoxLeft.Add(self.HSubSecond, flag=wx.EXPAND|wx.ALL)
        self.HSubSecond.Add(self.readButton,    flag=wx.CENTER|wx.EAST, proportion=1)
        self.HSubSecond.Add(self.gffButton,     border=1, proportion=1)
        self.VBoxLeft.Add((-1,15), flag=wx.EXPAND)
        self.VBoxLeft.Add(line, flag=wx.EXPAND|wx.EAST|wx.WEST)

        # Sets the THIRD frame
        # LINE
        line = wx.StaticLine(self, wx.HORIZONTAL)
        # BUTTON
        self.displayID = wx.NewId()
        self.displayButton = wx.Button(self, id=self.displayID, label="Display", size=(100,30))
        self.Bind(wx.EVT_BUTTON, self._display, self.displayButton)
        self.displayButton.Enable(False)

        # TEXT
        self.txtDisplay = wx.StaticText(self, label="3. Display a query", style=wx.ALIGN_LEFT)
        self.queryNameTxt = wx.StaticText(self, label="Query name", style=wx.ALIGN_LEFT)
        self.sepTxt = wx.StaticText(self, label="Separation (px)", style=wx.ALIGN_LEFT)
        self.zoomTxt = wx.StaticText(self, label="Zoom factor", style=wx.ALIGN_LEFT)
        self.yoffTxt = wx.StaticText(self, label="Y Offset", style=wx.ALIGN_LEFT)
        self.chrTxt = wx.StaticText(self, label="Chromosome color", style=wx.ALIGN_LEFT)
        self.plusTxt = wx.StaticText(self, label="+ strand color", style=wx.ALIGN_LEFT)
        self.minTxt = wx.StaticText(self, label="- strand color", style=wx.ALIGN_LEFT)
        self.showInfoTxt = wx.StaticText(self, label="Show block informations", style=wx.ALIGN_LEFT)
        self.showLinksTxt = wx.StaticText(self, label="Show links on chromosome", style=wx.ALIGN_LEFT)

        # INPUT
        self.queryInput = wx.TextCtrl(self)
        self.queryInput.Enable(False)
        self.sepInput = wx.TextCtrl(self)
        self.sepInput.Enable(False)
        self.zoomInput = wx.TextCtrl(self)
        self.zoomInput.Enable(False)
        self.yoffInput = wx.TextCtrl(self)
        self.yoffInput.Enable(False)
        self.colorInputChromosome = wx.NewId()
        self.colorChromosome = [0,0,255]
        self.chrInput = wx.Button(self, id=self.colorInputChromosome, label="Pick color")
        self.chrInput.Enable(False)
        self.Bind(wx.EVT_BUTTON, self._pick_color, self.chrInput)
        self.colorPlus = [255,0,0]
        self.colorInputPlus = wx.NewId()
        self.plusInput = wx.Button(self, id=self.colorInputPlus, label="Pick color")
        self.plusInput.Enable(False)
        self.Bind(wx.EVT_BUTTON, self._pick_color, self.plusInput)
        self.colorMinus = [0,255,0]
        self.colorInputMinus = wx.NewId()
        self.minInput = wx.Button(self, id=self.colorInputMinus, label="Pick color")
        self.minInput.Enable(False)
        self.Bind(wx.EVT_BUTTON, self._pick_color, self.minInput)
        self.showInfoBox=wx.CheckBox(self)
        self.showInfoBox.Enable(False)
        self.showLinksBox = wx.CheckBox(self)
        self.showLinksBox.Enable(False)

        # OUTPUT
        self.logout = wx.TextCtrl(self, value="Outputs are printed here\n", style = wx.TE_READONLY | wx.TE_MULTILINE) # Sets self as parent

        # HORIZONTAL SUBLAYOUTS
        self.HSub0 = wx.BoxSizer(wx.HORIZONTAL) # Query name
        self.HSub1 = wx.BoxSizer(wx.HORIZONTAL) # Separation
        self.HSub2 = wx.BoxSizer(wx.HORIZONTAL) # Zoom factor
        self.HSub3 = wx.BoxSizer(wx.HORIZONTAL) # Yoffset
        self.HSub4 = wx.BoxSizer(wx.HORIZONTAL) # Chr col
        self.HSub5 = wx.BoxSizer(wx.HORIZONTAL) # + col
        self.HSub6 = wx.BoxSizer(wx.HORIZONTAL) # - col
        self.HSub7 = wx.BoxSizer(wx.HORIZONTAL) # show info
        self.HSub8 = wx.BoxSizer(wx.HORIZONTAL) # show links

        # COLOR INFO
        self.colChromPanel = wx.Panel(self)
        self.colChromPanel.SetBackgroundColour(self.colorChromosome)
        self.colPlusPanel = wx.Panel(self)
        self.colPlusPanel.SetBackgroundColour(self.colorPlus)
        self.colMinusPanel = wx.Panel(self)
        self.colMinusPanel.SetBackgroundColour(self.colorMinus)

        # LAYOUT
        self.VBoxLeft.Add(self.txtDisplay,  flag=wx.EAST, border=2)
        self.VBoxLeft.Add((-1,5),           flag=wx.EXPAND)
        self.VBoxLeft.Add(self.HSub0,       flag=wx.EXPAND|wx.ALL)
        self.VBoxLeft.Add(self.HSub1,       flag=wx.EXPAND|wx.ALL)
        self.VBoxLeft.Add(self.HSub2,       flag=wx.EXPAND|wx.ALL)
        self.VBoxLeft.Add(self.HSub3,       flag=wx.EXPAND|wx.ALL)
        self.VBoxLeft.Add(self.HSub4,       flag=wx.EXPAND|wx.ALL)
        self.VBoxLeft.Add(self.HSub5,       flag=wx.EXPAND|wx.ALL)
        self.VBoxLeft.Add(self.HSub6,       flag=wx.EXPAND|wx.ALL)
        self.VBoxLeft.Add(self.HSub7,       flag=wx.EXPAND|wx.ALL)
        self.VBoxLeft.Add(self.HSub8,       flag=wx.EXPAND|wx.ALL)
        self.VBoxLeft.Add((-1,5),           flag=wx.EXPAND)
        self.VBoxLeft.Add(self.displayButton, flag=wx.EXPAND|wx.ALL, border=2)
        self.VBoxLeft.Add(self.logout, flag=wx.CENTER|wx.EXPAND, border=2, proportion=1)

        self.HSub0.Add(self.queryNameTxt,   flag=wx.CENTER|wx.EAST, proportion=1)
        self.HSub1.Add(self.sepTxt,         flag=wx.CENTER|wx.EAST, proportion=1)
        self.HSub2.Add(self.zoomTxt,        flag=wx.CENTER|wx.EAST, proportion=1)
        self.HSub3.Add(self.yoffTxt,        flag=wx.CENTER|wx.EAST, proportion=1)
        self.HSub4.Add(self.chrTxt,         flag=wx.CENTER|wx.EAST, proportion=3)
        self.HSub5.Add(self.plusTxt,        flag=wx.CENTER|wx.EAST, proportion=3)
        self.HSub6.Add(self.minTxt,         flag=wx.CENTER|wx.EAST, proportion=3)
        self.HSub7.Add(self.showInfoTxt,    flag=wx.CENTER|wx.EAST, proportion=1)
        self.HSub8.Add(self.showLinksTxt,   flag=wx.CENTER|wx.EAST, proportion=1)

        self.HSub0.Add(self.queryInput,     border=1, proportion=1)
        self.HSub1.Add(self.sepInput,       border=1, proportion=1)
        self.HSub2.Add(self.zoomInput,      border=1, proportion=1)
        self.HSub3.Add(self.yoffInput,      border=1, proportion=1)
        self.HSub4.Add(self.chrInput,       border=1, proportion=2)
        self.HSub5.Add(self.plusInput,      border=1, proportion=2)
        self.HSub6.Add(self.minInput,       border=1, proportion=2)
        self.HSub7.Add(self.showInfoBox,    border=1, proportion=1)
        self.HSub8.Add(self.showLinksBox,   border=1, proportion=1)

        self.HSub4.Add(self.colChromPanel,  border=1, proportion=1, flag=wx.EXPAND|wx.ALL|wx.CENTER)
        self.HSub5.Add(self.colPlusPanel,   border=1, proportion=1, flag=wx.EXPAND|wx.ALL|wx.CENTER)
        self.HSub6.Add(self.colMinusPanel,  border=1, proportion=1, flag=wx.EXPAND|wx.ALL|wx.CENTER)

        """
         __      ______            _____  _       _     _
         \ \    / /  _ \          |  __ \(_)     | |   | |
          \ \  / /| |_) | _____  _| |__) |_  __ _| |__ | |_
           \ \/ / |  _ < / _ \ \/ /  _  /| |/ _` | '_ \| __|
            \  /  | |_) | (_) >  <| | \ \| | (_| | | | | |_
             \/   |____/ \___/_/\_\_|  \_\_|\__, |_| |_|\__|
                                             __/ |
                                            |___/
        """#################################################

        self.htmlPanel = HTMLPanel(self)
        self.VBoxRight.Add(self.htmlPanel, flag=wx.EXPAND|wx.ALL, border=2, proportion=1)
        #self.htmlPanel.displaySVG("../../SADisplay/outgraph.svg") # DEBUG

        """
          ________      ________ _   _ _______ _____
         |  ____\ \    / /  ____| \ | |__   __/ ____|
         | |__   \ \  / /| |__  |  \| |  | | | (___
         |  __|   \ \/ / |  __| | . ` |  | |  \___ \
         | |____   \  /  | |____| |\  |  | |  ____) |
         |______|   \/   |______|_| \_|  |_| |_____/
        """##########################################

        # Binds events
        self.Bind(wx.EVT_MENU, self._quit, fileExit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self._open, self.fileOpen, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self._help, helpHelp, id=wx.ID_HELP)
        self.Bind(wx.EVT_MENU, self._about, helpAbout, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self._import_gff, self.importGFF, id=self.impgffID)
        self.Bind(wx.EVT_MENU, self._reset, self.closeAndReset, id=self.reset_ID)

        """
          _____        __      ____
         |_   _|      / _|    |  _ \
           | |  _ __ | |_ ___ | |_) | __ _ _ __
           | | | '_ \|  _/ _ \|  _ < / _` | '__|
          _| |_| | | | || (_) | |_) | (_| | |
         |_____|_| |_|_| \___/|____/ \__,_|_|
        """##################################

        # Sets an infobar
        # Hide the message after 3000ms
        self.infoBar = AutoDismissInfo(self, 3000) # Sets self as parent for the infobar
        self.infoBar.AddButton(wx.ID_HELP, "Help!")
        self.ID_HIDEMESSAGE = wx.NewId()
        self.infoBar.AddButton(self.ID_HIDEMESSAGE, "Hide")
        self.layout.Add(self.infoBar, flag=wx.EXPAND|wx.ALL, border=2, proportion=0) # ALWAYS AT POSITION 3
        self.infoBar.ShowMessage("Hello! Welcome to SAVi. Need any help?", 8000)
        self.infoBar.Bind(wx.EVT_BUTTON, self._help, id=wx.ID_HELP) # OK DONE

    """
        ________      ________ _   _ _______ _____
       |  ____\ \    / /  ____| \ | |__   __/ ____|
       | |__   \ \  / /| |__  |  \| |  | | | (___
       |  __|   \ \/ / |  __| | . ` |  | |  \___ \
       | |____   \  /  | |____| |\  |  | |  ____) |
       |______|   \/   |______|_| \_|  |_| |_____/
    """############################################

    def _quit(self, id) : # OK DONE
        """Closes the application"""
        self.Close()

    def _open(self, id) : # OK DONE
        OPENED_FILE = self.openFileDialog()
        # DEBUG
        #print('Opening from dialog\nfilename: {}'.format(self.CURRENTFILE))

        # TESTS IF FILE IS CORRUPTor NOT EXISTING or WHATEVER
        if not self.checkFile(OPENED_FILE):
            # Prints to info that path not exists OR file is corrupt
            # Returns to idling
            return
        else: # IF FILE IS CORRECT:
            # CHECK DB OR PAF FILE
            ext = os.path.splitext(OPENED_FILE)[1]
            if ext == ".paf" :
                self._check_PAF(OPENED_FILE) # CHECKS THE FILE AND LOAD IT

            elif ext == ".db" :
                self._check_DB(OPENED_FILE) # CHECKS THE FILE AND LOAD IT
            else :
                return

    def _reset(self, id) : # OK DONE
        self.logout.Clear()                                     # Clears the log
        self.logout.AppendText("Outputs are printed here\n")    # Reset log

        # RESETS LOCAL VARIABLES
        self.currentMode = None         # 0 = None LOADED, 1 = PAF LOADED, 2 = DB LOADED
        self.currentPAF = None          # current PAF file
        self.currentDB = None           # current SARead DATABASE
        self.GENEMARKS_FOUND = False    # Sets a GENEMARKS found bool
        self.ALIGNED_FOUND = False      # Sets a ALIGNED found bool

        # DISABLES ALL THE WIDGETS
        self.readButton.Enable(False)                   # Disables reading
        self.gffButton.Enable(False)                    # Disables gff import from button
        self.toolbar.EnableTool(self.impgffID, False)   # Disables gff import from toolbar
        self.importGFF.Enable(False)                    # Disables gff import from filemenu
        self.queryInput.Enable(False)                   # Disables name input
        self.sepInput.Enable(False)                     # Disables separation input
        self.zoomInput.Enable(False)                    # Disables zoom factor input
        self.yoffInput.Enable(False)                    # Disables y offest input
        self.chrInput.Enable(False)                     # Disables chromosome color input
        self.plusInput.Enable(False)                    # Disables + strand color input
        self.minInput.Enable(False)                     # Disables - strand color input
        self.showInfoBox.Enable(False)                  # Disables show info tick
        self.showLinksBox.Enable(False)                 # Disables show links tick
        self.displayButton.Enable(False)                # Disables SADisplay command start

        # ENABLES WIDGETS
        self.fileOpen.Enable(True)                  # Inactivate filemenu open
        self.toolbar.EnableTool(wx.ID_OPEN, True)   # Inactivate toolbar open
        self.openButton.Enable(True)                # Inactivate open button

    def _read(self, id) :  # OK DONE
        # self.logout.Clear()                               # Clears the log
        self.logout.AppendText("#Starting SARead...\n")      # Say we start to read
        # Build the command and removes spaces
        command = "../SARead/SARead {}".format(self.rename_spac(self.currentPAF))
        # Prints which command is used
        self.logout.AppendText("Command used:\n${}\n".format(command))

        # DISABLE TOOLS AND BUTTONS
        self.readButton.Enable(False)

        # Starts SARead
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        self.logout.SetDefaultStyle(wx.TextAttr(colText=wx.RED))
        while True :                                            # Waits and prints cout
            line = proc.stdout.readline()                       # Reads line from stdout
            wx.Yield()                                          # Gives python priority on subprocess
            if line.strip() == "" :                             # If line is empty
                pass
            else :                                              # Else prints the line
                if len(line) > 0 :
                    self.logout.AppendText(">")
                    self.logout.AppendText(line)
            if not line :
                break                                           # If there is no piping in anymore
            proc.wait()                                         # Waits for a new piping in
        self.logout.SetDefaultStyle(wx.TextAttr(colText=wx.BLACK))
        self.logout.AppendText("#Finished\n\n")
        # NOW THE DATABASE WAS CREATED
        self._load_db(self.currentPAF + ".db")

    def _display(self, id) :
        DISPLAY = True                                              # Sets a DISPLAY bool
        showinfo = bool(self.showInfoBox.GetValue())                # Gets the value of show info
        showlinks = bool(self.showLinksBox.GetValue())              # Gets the value of show links
        try :
            qname = str(self.queryInput.GetValue())                 # Gets the value of query input
            if not self.check_input_value_type(qname, "string") :   # Checks the value type
                DISPLAY = False                                     # Sets display bool to false
                self.queryInput.SetBackgroundColour((200,0,0))      # Sets background color to red
                self.queryInput.Refresh()
            else :
                self.queryInput.SetBackgroundColour((255,255,255))  # Refreshes background color to white
                self.queryInput.Refresh()
        except :                                                    # If cannot get input value
            DISPLAY = False                                         # Sets display bool to false
            self.queryInput.SetBackgroundColour((200,0,0))          # Sets background color to red
            self.queryInput.Refresh()

        try :
            sep = int(self.sepInput.GetValue())                     # Gets the value of separation
            if not self.check_input_value_type(sep, "int") :        # Checks the value type
                DISPLAY = False                                     # Sets display bool to false
                self.sepInput.SetBackgroundColour((200,0,0))        # Sets background color to red
                self.sepInput.Refresh()
            else :
                self.sepInput.SetBackgroundColour((255,255,255))    # Refreshes background color to white
                self.sepInput.Refresh()
        except :                                                    # If cannot get input value
            DISPLAY = False                                         # Sets display bool to false
            self.sepInput.SetBackgroundColour((200,0,0))            # Sets background color to red
            self.sepInput.Refresh()

        try :
            zoom = int(self.zoomInput.GetValue())                   # Gets the value of zoom
            if not self.check_input_value_type(zoom, "int") :       # Checks the value type
                DISPLAY = False                                     # Sets display bool to false
                self.zoomInput.SetBackgroundColour((200,0,0))       # Sets background color to red
                self.zoomInput.Refresh()
            else :
                self.zoomInput.SetBackgroundColour((255,255,255))   # Refreshes background color to white
                self.zoomInput.Refresh()
        except :
            DISPLAY = False                                         # Sets display bool to false
            self.zoomInput.SetBackgroundColour((200,0,0))           # Sets background color to red
            self.zoomInput.Refresh()

        try :
            yoff = int(self.yoffInput.GetValue())                   # Gets the value of y offset
            if not self.check_input_value_type(yoff, "int") :       # Checks the value type
                DISPLAY = False                                     # Sets display bool to false
                self.yoffInput.SetBackgroundColour((200,0,0))       # Sets background color to red
                self.yoffInput.Refresh()
            else :
                self.yoffInput.SetBackgroundColour((255,255,255))   # Refreshes background color to white
                self.yoffInput.Refresh()
        except :
            DISPLAY = False                                         # Sets display bool to false
            self.yoffInput.SetBackgroundColour((200,0,0))           # Sets background color to red
            self.yoffInput.Refresh()

        # IF ALL VALUES ARE VALID STRINGS OR INTS
        if DISPLAY :
            """ DEBUG
            self.logout.AppendText("$Query\t\t\t\t{}\n".format(qname))
            self.logout.AppendText("$Separation\t\t\t{}\n".format(sep))
            self.logout.AppendText("$Zoom Factor\t\t\t{}\n".format(zoom))
            self.logout.AppendText("$Y Offset\t\t\t{}\n".format(yoff))
            self.logout.AppendText("$Show Information\t\t{}\n".format(showinfo))
            self.logout.AppendText("$Show Links\t\t\t{}\n".format(showlinks))
            self.logout.AppendText("$Chromosome color\t{}\n".format(self.colorChromosome))
            self.logout.AppendText("$Relative + color\t\t{}\n".format(self.colorPlus))
            self.logout.AppendText("$Relative - color\t\t{}\n".format(self.colorMinus))
            """

            self.logout.AppendText("#Starting SADisplay...\n")

            chrcolstr = "{},{},{}".format(self.colorChromosome[0],self.colorChromosome[1],self.colorChromosome[2])
            pluscolstr = "{},{},{}".format(self.colorPlus[0],self.colorPlus[1],self.colorPlus[2])
            minuscolstr = "{},{},{}".format(self.colorMinus[0],self.colorMinus[1],self.colorMinus[2])

            info = "y"
            if not showinfo :
                info = "n"

            links = "y"
            if not showlinks :
                links = "n"

            cmd = "../SADisplay/SADisplay {} {} {} {} {} {} {} {} {} {}".format(self.rename_spac(self.currentDB), sep, zoom, yoff, links, chrcolstr, pluscolstr, minuscolstr, info, qname)
            self.logout.AppendText("Command used:\n${}\n".format(cmd))          # Logs the cmd
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)    # Starts SADisplay
            self.logout.SetDefaultStyle(wx.TextAttr(colText=wx.RED))            # Sets the text to red
            while True :                                                        # Waits and prints cout
                line = proc.stdout.readline()                                   # Gives python priority on subprocess
                wx.Yield()                                                      # Outputs line
                if line.strip() == "" :                                         # If line is empty
                    pass                                                        # Do nothing
                else :                                                          # If line is not empty
                    if len(line) > 0 :                                          # If the line is > 0
                        self.logout.AppendText(">")
                        self.logout.AppendText(line)                            # Prints the line
                if not line :                                                   # If there is no piping in anymore
                    break                                                       # break the while
                proc.wait()                                                     # Waits for a new piping in

            self.logout.SetDefaultStyle(wx.TextAttr(colText=wx.BLACK))          # Sets the text to black
            SVGFilePath = os.path.join(os.path.dirname(self.rename_spac(self.currentDB)), qname + ".svg")
            self.htmlPanel.displaySVG(SVGFilePath, qname, zoom)
            self.logout.AppendText("#Finished\n\n")
            return

    def _help(self, id) :
        print("Help!")
        # Toplevel
        pass

    def _about(self, id) :
        print("About!")
        # Toplevel
        pass

    def _load_paf(self, path) :
        self.currentPAF = os.path.abspath(path)                          # Sets current PAF variable
        self.logout.AppendText("Loading PAF file: {}\n".format(self.currentPAF))
        # DISABLE PREVIOUS USES
        self.toolbar.EnableTool(wx.ID_OPEN, False)      # Inactivate toolbar open
        self.fileOpen.Enable(False)                     # Inactivate filemenu open
        self.openButton.Enable(False)                   # Inactivate open button
        # ENABLE READ AND Import GFF
        filename = os.path.basename(path)               # Gets filename
        self.readButton.SetLabel("Read " + filename)    # Changes button label
        self.readButton.Enable(True)                    # Enables reading
        self.gffButton.Enable(True)                     # Enables gff import from button
        self.toolbar.EnableTool(self.impgffID, True)    # Enables gff import from toolbar
        self.importGFF.Enable(True)                     # Enables gff import from filemenu

    def _load_db(self, path) :
        self.currentDB = os.path.abspath(path)
        self.logout.AppendText("Loading SAVi database: {}\n".format(self.currentDB))

        # DISABLES THE WIDGETS
        self.toolbar.EnableTool(wx.ID_OPEN, False)      # Inactivate toolbar open
        self.fileOpen.Enable(False)                     # Inactivate filemenu open
        self.openButton.Enable(False)                   # Inactivate open button
        self.readButton.Enable(False)                   # Disables reading
        self.gffButton.Enable(False)                    # Disables gff import from button
        self.toolbar.EnableTool(self.impgffID, False)   # Disables gff import from toolbar
        self.importGFF.Enable(False)                    # Disables gff import from filemenu
        # ENABLE THE WIDGETS
        self.queryInput.Enable(True)        # Enables query name input
        self.sepInput.Enable(True)          # Enables separation input
        self.zoomInput.Enable(True)         # Enables zoom factor input
        self.yoffInput.Enable(True)         # Enables y offset input
        self.chrInput.Enable(True)          # Enables chromosome color input
        self.plusInput.Enable(True)         # Enables + strand color input
        self.minInput.Enable(True)          # Enables - strand color input
        self.showInfoBox.Enable(True)       # Enables show info tick
        self.showLinksBox.Enable(True)      # Enables show links tick
        self.displayButton.Enable(True)     # Enables SADisplay command start

    def _pick_color(self, event) :
        colorBox = wx.ColourDialog(None)
        answer = colorBox.ShowModal()
        if answer == wx.ID_OK :
            if event.Id == self.colorInputChromosome :
                self.colorChromosome = colorBox.GetColourData().GetColour().Get(includeAlpha=False)
                self.colChromPanel.SetBackgroundColour(self.colorChromosome)
                #print(self.colorChromosome)
            elif event.Id == self.colorInputPlus :
                self.colorPlus = colorBox.GetColourData().GetColour().Get(includeAlpha=False)
                self.colPlusPanel.SetBackgroundColour(self.colorPlus)
                #print(self.colorPlus)
            elif event.Id == self.colorInputMinus :
                self.colorMinus = colorBox.GetColourData().GetColour().Get(includeAlpha=False)
                self.colMinusPanel.SetBackgroundColour(self.colorMinus)
                #print(self.colorMinus)
        colorBox.Destroy()
        return

    def _import_gff(self, id) :
        self.logout.AppendText("Not implemented yet...\n")
        pass

    def _check_DB(self, path) : # # CHECKS THE FILE AND CALL -> LOAD DB OR NOTHING
        self.logout.AppendText("Checking database...\n")
        self.logout.AppendText("Trying to connect to the database\n")

        try:
            conn = sqlite3.connect(path)
        except sqlite3.Error as e :
            self.logout.AppendText("ERROR: Database connection failure: {}\n".format(e))
            return

        cur = conn.cursor()

        # GETS ALL DIFFERENT BLAST QUERIES -> stores them to a list
        sqlcmd = "SELECT name FROM sqlite_master WHERE type='table';"
        try :
            cur.execute(sqlcmd)
        except sqlite3.Error as e :
            self.logout.AppendText("ERROR: {}\n".format(e))
            return

        tables = [x[0] for x in cur.fetchall()]

        if len(tables) == 0 :
            self.logout.AppendText("WARNING: No tables detected, database is useless\n")
            return

        if "ALIGNED" in tables :
            self.logout.AppendText("ALIGNED table found!\n")
            self.ALIGNED_FOUND = True
        else :
            self.logout.AppendText("WARNING: ALIGNED is not found, database is useless\n")
            return

        if "GENEMARKS" in tables :
            self.logout.AppendText("GENEMARKS table found!\n")
            self.GENEMARKS_FOUND = True

        conn.close() # Closes DB
        self.logout.AppendText("Database is OK!\n")
        self._load_db(path)

    def _check_PAF(self, path) : # CHECKS THE FILE AND CALL -> LOAD DB OR LOAD PAF OR NOTHING
        # search in directory if file exists
        if self.checkFile(path+".db") :
            # DIALOG WITH THREE CHOICES -> CANCEL OR LOAD DB OR OVERWRITE IT
            yesNoBox = wx.MessageDialog(None, "A database was found: {}\nDo you want to rebuild it?".format(path+".db"), "Question", wx.CENTRE|wx.YES_NO|wx.CANCEL)
            yesNoBox.SetYesNoCancelLabels("Rebuild", "Load found database", "Do nothing")
            answer = yesNoBox.ShowModal()
            yesNoBox.Destroy()

            if answer == wx.ID_CANCEL : # RETURNS AT STEP 0
                return
            elif answer == wx.ID_NO : # LOADS DIRECTLY THE DATABASE
                self._check_DB(path+".db")
            else :
                # Renames the db file
                now = datetime.datetime.now()
                newFileName = path + ".db.{}-{}-{}h{}".format(now.month, now.day, now.hour, now.minute)
                self.logout.AppendText("Detected DB was moved to: {}\n".format(newFileName))

                try :
                    os.rename(path + ".db", newFileName)
                    # Now we can proceed with opening from .paf file
                    self._load_paf(path)
                except :
                    self.logout.AppendText("WARNING: DB could not be moved!\n")
                    return
        # IF NO DB IS FOUND
        else :
            # Opens the paf file
            self._load_paf(path)
            return

    """
     ______ _    _ _   _  _____ _______ _____ ____  _   _  _____
    |  ____| |  | | \ | |/ ____|__   __|_   _/ __ \| \ | |/ ____|
    | |__  | |  | |  \| | |       | |    | || |  | |  \| | (___
    |  __| | |  | | . ` | |       | |    | || |  | | . ` |\___ \
    | |    | |__| | |\  | |____   | |   _| || |__| | |\  |____) |
    |_|     \____/|_| \_|\_____|  |_|  |_____\____/|_| \_|_____/
    """###########################################################

    def check_input_value_type(self, value, input_type) :
        if input_type == "bool" :
            if type(value) == type(True) :
                return True
            else :
                return False
        if input_type == "int" :
            if type(value) == type(1) :
                return True
            else :
                return False
        if input_type == "float" :
            if type(value) == type(0.1) :
                return True
            else :
                return False
        if input_type == "string" :
            if type(value) == type("string") :
                if len(value) > 0 :
                    return True
                else :
                    return False
            else :
                return False

    def checkFile(self, path) :
        #print("PATH: {}".format(path))
        if path == None :
            return False
        else :
            try :
                if os.path.isfile(path) : # Try avoids errors thrown if string is not pathlike
                    return True
                else :
                    return False
            except :
                print("Invalid path file path!") # Returns False as well
                return False                # OK DONE

    def openFileDialog(self) :
        # OPENS A DIALOG FOR FILE CHOOSING
        with wx.FileDialog(self, "Open a file", wildcard="PAF files (*.paf)|*.paf|DB files (*.db)|*.db|All files|*", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            # IN CASE OF CANCEL FROM USER
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return None
            # GATHERS PATHNAME
            pathname = fileDialog.GetPath()
            return pathname                 # OK DONE

    def rename_spac(self, filename) :
        return filename.replace(" ", "\ ") # OK DONE          # OK DONE

    def scaleBmp(self, bmp, width, height) :
        image = bmp.ConvertToImage()
        image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
        result = wx.Bitmap(image)
        return result   # OK DONE

def start_gui() :
    """This function starts SAVi"""
    SAVi = wx.App() # Sets a basix wx module
    # Creates the main frame of SAVi
    top = MainSAVi(None, title='SAVi')
    top.Show()
    # Starts the mainloop waiting for events
    SAVi.MainLoop()

if __name__ == '__main__':
    start_gui()
