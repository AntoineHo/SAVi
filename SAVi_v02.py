#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# GENERAL MODULES
import sys
import os
import platform
#import tempfile
import datetime

# GUI modules
from cefpython3 import cefpython as cef
import ctypes
try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

# Fix for PyCharm hints warnings
WindowUtils = cef.WindowUtils()

# Platforms
LINUX = (platform.system() == "Linux")
if not LINUX :
    sys.exit(1)

from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo

# PAF parsing modules
from parsepaf import *

# Drawing modules
from writesvg import *

from templates import MAIN_TEMPLATE_HTML


"""
 ______ _    _ _   _  _____ _______ _____ ____  _   _  _____
|  ____| |  | | \ | |/ ____|__   __|_   _/ __ \| \ | |/ ____|
| |__  | |  | |  \| | |       | |    | || |  | |  \| | (___
|  __| | |  | | . ` | |       | |    | || |  | | . ` |\___ \
| |    | |__| | |\  | |____   | |   _| || |__| | |\  |____) |
|_|     \____/|_| \_|\_____|  |_|  |_____\____/|_| \_|_____/
"""

def check_input_value_type(value, input_type) :
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

def checkFile(path) :
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

def rename_spac(filename) :
    return filename.replace(" ", "\ ")

#
# TK CLASSES
#

class BrowserFrame(tk.Frame):

    def __init__(self, mainframe):
        self.closing = False
        self.browser = None
        tk.Frame.__init__(self, mainframe)
        self.mainframe = mainframe
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
        self.bind("<Configure>", self.on_configure)
        """For focus problems see Issue #255 and Issue #535. """
        self.focus_set()

    def embed_browser(self):
        window_info = cef.WindowInfo()
        rect = [0, 0, self.winfo_width(), self.winfo_height()]
        window_info.SetAsChild(self.get_window_handle(), rect)
        cwd = os.getcwd()
        template = os.path.join(cwd, "template.html")
        f = open(template, 'w')
        f.write(MAIN_TEMPLATE_HTML)
        f.close()
        #print(template)
        self.browser = cef.CreateBrowserSync(window_info, url="file://{}".format(template))
        assert self.browser
        self.message_loop_work()

    def get_window_handle(self):
        if self.winfo_id() > 0:
            return self.winfo_id()
        else:
            raise Exception("Couldn't obtain window handle")

    def message_loop_work(self):
        cef.MessageLoopWork()
        self.after(10, self.message_loop_work)

    def on_configure(self, _):
        if not self.browser:
            self.embed_browser()

    def on_root_configure(self):
        # Root <Configure> event will be called when top window is moved
        if self.browser:
            self.browser.NotifyMoveOrResizeStarted()

    def on_mainframe_configure(self, width, height):
        if self.browser:
            self.browser.SetBounds(0, 0, width, height)
            self.browser.NotifyMoveOrResizeStarted()


    def on_focus_in(self, _):
        if self.browser:
            self.browser.SetFocus(True)

    def on_focus_out(self, _):
        """For focus problems see Issue #255 and Issue #535. """
        pass

    def on_root_close(self):
        #logger.info("BrowserFrame.on_root_close")
        if self.browser:
            self.browser.CloseBrowser(True)
            self.clear_browser_references()
        else:
            self.destroy()

    def clear_browser_references(self):
        # Clear browser references that you keep anywhere in your
        # code. All references must be cleared for CEF to shutdown cleanly.
        self.browser = None

class LifespanHandler(object):
    def __init__(self, tkFrame):
        self.tkFrame = tkFrame
    def OnBeforeClose(self, browser, **_):
        #logger.debug("LifespanHandler.OnBeforeClose")
        self.tkFrame.quit()

class LoadHandler(object):
    def __init__(self, browser_frame):
        self.browser_frame = browser_frame
    def OnLoadStart(self, browser, **_):
        pass

class FocusHandler(object):
    """For focus problems see Issue #255 and Issue #535. """
    def __init__(self, browser_frame):
        self.browser_frame = browser_frame
    def OnTakeFocus(self, next_component, **_):
        pass
    def OnSetFocus(self, source, **_):
        return True
    def OnGotFocus(self, **_):
        pass

class Console(): # create file like object
    """Taken from https://stackoverflow.com/questions/53721337/how-to-get-python-console-logs-on-my-tkinter-window-instead-of-a-cmd-window-whil"""
    def __init__(self, textbox): # pass reference to text widget
        self.textbox = textbox # keep ref
    def write(self, text):
        self.textbox.insert(tk.END, text) # write text to textbox
            # could also scroll to end of textbox here to make sure always visible
    def flush(self): # needed for file like object
        pass

#
# MAIN
#

class GUI(tk.Frame) :

    def __init__(self, parent) :

        # For stocking used .paf files
        self.files_to_remove = []

        # For Browser
        self.master = parent
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        self.master.bind("<Configure>", self.on_root_configure)
        #self.bind("<FocusIn>", self.on_focus_in)
        #self.bind("<FocusOut>", self.on_focus_out)

        # STATUS
        self.PAF_SELECTED = False
        self.PAF_LOADED = False
        self.PAF_DRAWN = False

        # Left frame contains entries and open button
        frame_1eft = tk.Frame(self.master, relief=tk.RAISED, borderwidth=2)
        frame_1eft.pack(side=tk.LEFT, fill=tk.BOTH, anchor=tk.NE, padx=2, pady=2)
        #frame_1eft.grid(row=0, column=0, sticky=('NSWE'))

        # Filling of frame_left
        left_sub1 = tk.Frame(frame_1eft)
        left_sub1.pack(fill=tk.X, anchor=tk.NW)
        self.open_button = tk.Button(left_sub1, text="Open", command=self.open_paf)
        self.open_button.pack(side=tk.LEFT, anchor=tk.W, padx=5, pady=5)

        self.file_labeltext = tk.StringVar()
        self.file_labeltext.set("None")
        self.file_label = tk.Label(left_sub1, textvariable=self.file_labeltext)
        self.file_label.pack(side=tk.LEFT, anchor=tk.W, padx=1, pady=1)

        sep1 = ttk.Separator(frame_1eft, orient='horizontal')
        sep1.pack(fill=tk.X, anchor=tk.N, pady=10)

        left_sub2 = tk.Frame(frame_1eft)
        left_sub2.pack(fill=tk.X, anchor=tk.NW)
        target_label = tk.Label(left_sub2, text="Target", width=6)
        target_label.pack(side=tk.LEFT, anchor=tk.NW, padx=5, pady=5)

        left_sub3 = tk.Frame(frame_1eft)
        left_sub3.pack(fill=tk.X, anchor=tk.NW)
        self.entry1 = tk.Entry(left_sub3)
        self.entry1.pack(side=tk.LEFT, fill=tk.X, anchor=tk.NW, padx=5)

        sep2 = ttk.Separator(frame_1eft, orient='horizontal')
        sep2.pack(fill=tk.X, anchor=tk.N, pady=10)

        left_sub4 = tk.Frame(frame_1eft)
        left_sub4.pack(fill=tk.X, anchor=tk.NW)

        self.read_button = tk.Button(left_sub4, text="Read", command=self.read_paf)
        self.read_button.pack(side=tk.LEFT, anchor=tk.W, padx=5, pady=5)

        self.draw_button = tk.Button(left_sub4, text="Draw", command=self.draw_paf)
        self.draw_button.pack(side=tk.LEFT, anchor=tk.W, padx=5, pady=5)

        left_sub5 = tk.Frame(frame_1eft)
        left_sub5.pack(fill=tk.X, anchor=tk.N)

        self.save_button = tk.Button(left_sub5, text="Save .svg", command=self.save_svg)
        self.save_button.pack(anchor=tk.W, padx=5, pady=5)

        self.save_html = tk.Button(left_sub5, text="Save .html", command=self.save_html)
        self.save_html.pack(anchor=tk.W, padx=5, pady=5)

        sep3 = ttk.Separator(frame_1eft, orient='horizontal')
        sep3.pack(fill=tk.X, anchor=tk.N, pady=10)

        left_sub6 = tk.Frame(frame_1eft)
        left_sub6.pack(fill=tk.BOTH, anchor=tk.N)

        # Right frame contains .SVG file
        frame_right = tk.Frame(self.master, relief=tk.RAISED, borderwidth=2)
        frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, anchor=tk.N, padx=2, pady=2, expand=True)
        #frame_right.grid(row=0, column=1, sticky=('NSWE'))
        frame_right.bind("<Configure>", self.on_configure)

        self.browser_frame = BrowserFrame(frame_right)
        self.browser_frame.pack(fill=tk.BOTH, expand=True) # side=tk.LEFT, anchor=tk.NW,

        #### CONSOLE
        self.log = tk.Text(left_sub6)#, state='disabled')
        self.log.pack(fill=tk.BOTH, anchor=tk.NW, padx=5, pady=5, expand=True)
        pl = Console(self.log)
        # replace sys.stdout with our object
        sys.stdout = pl

    def open_paf(self) :
        """Load a .paf file to draw"""
        filetypes = (('paf files', '*.paf'), ('All files', '*.*'))
        self.filename = fd.askopenfilename(title='Open a file', initialdir='/', filetypes=filetypes)
        #showinfo(title='Selected File', message=filename)
        self.file_labeltext.set(os.path.split(self.filename)[-1])
        self.PAF_SELECTED = True

    def read_paf(self) :
        """Read data in the loaded .paf file"""
        if not self.PAF_SELECTED :
            print("WARNING: no .paf file selected, please open a file!")
            return

        self.data = read_paf(self.filename)
        self.PAF_LOADED = True
        print(self.data.head(5))

    def draw_paf(self) :
        """Draw .paf file"""
        if not self.PAF_SELECTED :
            print("WARNING: no .paf file selected, please open a file!")
            return
        elif not self.PAF_LOADED :
            print("WARNING: .paf file is selected but not loaded, please read before drawing")
            return

        # Read target in entry
        self.current_target = self.entry1.get()
        if self.current_target == "" : # empty target
            print("WARNING: please choose a target to draw alignments...")
            return

        print("Drawing...")
        self.HTML, self.SVG = draw_svg_in_memory(data = self.data, target = self.current_target)
        f = open(self.filename + ".temp.html", 'w')
        f.write(self.HTML)
        f.close()
        self.files_to_remove.append(self.filename + ".temp.html")
        self.browser_frame.browser.LoadUrl("file://"+self.filename+".temp.html")

        self.PAF_DRAWN = True


    def save_svg(self) :
        if not  self.PAF_SELECTED or not self.PAF_LOADED or not self.PAF_DRAWN :
            print("WARNING: no drawing found to save...")
            return
        else :
            savefile = fd.asksaveasfile(mode='w', defaultextension=".svg")
            savefile.write(self.SVG)
            savefile.close()
            print("Saved .svg to: {}".format(savefile))

    def save_html(self) :
        if not  self.PAF_SELECTED or not self.PAF_LOADED or not self.PAF_DRAWN :
            print("WARNING: no drawing found to save...")
            return
        else :
            savefile = fd.asksaveasfile(mode='w', defaultextension=".html")
            savefile.write(self.HTML)
            savefile.close()
            print("Saved .html to: {}".format(savefile))

    #### METHODS USED BY BROWSER_FRAME
    def on_root_configure(self, _):
        if self.browser_frame:
            self.browser_frame.on_root_configure()

    def on_configure(self, event):
        #logger.debug("MainFrame.on_configure")
        if self.browser_frame:
            width = event.width
            height = event.height
            self.browser_frame.on_mainframe_configure(width, height)

    def on_close(self):
        if self.browser_frame:
            self.browser_frame.on_root_close()
            self.browser_frame = None

        cwd = os.getcwd()
        template = os.path.join(cwd, "template.html")
        self.files_to_remove.append(template)

        for file in self.files_to_remove :
            os.remove(file)
        
        self.master.destroy()




if __name__ == '__main__':
    assert cef.__version__ >= "55.3", "CEF Python v55.3+ required to run this"
    sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error

    window = tk.Tk()
    window.minsize(1000,500)
    window.columnconfigure(0, weight=1)
    window.columnconfigure(1, weight=1)
    window.rowconfigure(0, weight=1)
    window.title("SAVi")

    cef.Initialize()

    interface = GUI(window)
    window.mainloop()

    cef.Shutdown()
