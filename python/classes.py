# -*- coding: utf-8 -*-
"""
Created on Fri Feb 23 18:24:53 2018

@author: Pc-Antoine2
"""

# LOCAL MODULES
#import globV

# GENERAL MODULES
import wx
import wx.html2 as webview # REQUIRES libwebkitgtk-dev & glib-networking
import os

class AutoDismissInfo(wx.InfoBar) :
    """This class is used to dismiss info after some time"""
    def __init__(self, parent, hideAfter=-1) :
        super(AutoDismissInfo, self).__init__(parent) # Inits an infobar
        self.timer = wx.Timer(self)
        self.limit = hideAfter

        self.Bind(wx.EVT_TIMER, lambda event: self.Dismiss(), self.timer)

    def ShowMessage(self, msg, flags) :
        if self.timer.IsRunning() :
            self.timer.Stop()

        super(AutoDismissInfo, self).ShowMessage(msg, flags)

        if self.limit > 0 :
            self.timer.Start(self.limit, True)


class AboutGUI :
    """This class contains the About GUI builder and functions"""
    def __init__(self) :
        pass

class DocGUI :
    """This class contains the About GUI builder and functions"""
    def __init__(self) :
        pass

class HTMLPanel(wx.Panel) :
    """This class renders HTML code fed from a string"""
    def __init__(self, parent, SVGFilePath="None") :
        wx.Panel.__init__(self, parent)
        self.path = SVGFilePath

        self.frame = self.GetTopLevelParent()
        self.titleBase = self.frame.GetTitle()

        self.sizer = wx.BoxSizer(wx.VERTICAL) # Sets the vertical sizer for the whole panel
        self.HSub = wx.BoxSizer(wx.HORIZONTAL) # Sets the sub sizer for zooming around

        self.wv = webview.WebView.New(self) # Sets the webview
        self.wv.SetZoomType(webview.WEBVIEW_ZOOM_TYPE_LAYOUT)
        self.zoom_factor = [webview.WEBVIEW_ZOOM_TINY, webview.WEBVIEW_ZOOM_SMALL, webview.WEBVIEW_ZOOM_MEDIUM, webview.WEBVIEW_ZOOM_LARGE, webview.WEBVIEW_ZOOM_LARGEST]
        self.zoom_factor_lst = ["Smallest", "Small", "Normal", "Large", "Largest"]
        self.zoom_idx = 2 # MEDIUM
        self.wv.SetZoom(self.zoom_factor[self.zoom_idx])

        # Txtctrl
        self.currentSVGshowcase = wx.TextCtrl(self, style=wx.TE_READONLY|wx.TE_CENTER)
        self.currentSVGshowcase.Enable(False)
        self.sizer.Add(self.currentSVGshowcase, flag=wx.EXPAND|wx.EAST|wx.WEST, border=2)

        # main frame
        self.sizer.Add(self.wv, flag=wx.EXPAND|wx.ALL, proportion=10, border=2)
        self.SetSizer(self.sizer)

        # Button sizer
        self.sizer.Add(self.HSub, flag=wx.EXPAND|wx.EAST|wx.WEST, border=2)

        # Zoom btn
        bmp = self.scaleBmp(wx.Bitmap('rsc/zoom-in.png'), 20, 20)
        btn = wx.BitmapButton(self, -1, bitmap=bmp, size=(bmp.GetWidth()+15, bmp.GetHeight()+15))
        self.Bind(wx.EVT_BUTTON, self.OnZoomButton, btn)
        self.HSub.Add(btn, 0, wx.EXPAND|wx.ALL, 2)

        # DeZoom btn
        bmp = self.scaleBmp(wx.Bitmap('rsc/zoom-out.png'), 20, 20)
        btn = wx.BitmapButton(self, -1, bitmap=bmp, size=(bmp.GetWidth()+15, bmp.GetHeight()+15))
        self.Bind(wx.EVT_BUTTON, self.OnDezoomButton, btn)
        self.HSub.Add(btn, 0, wx.EXPAND|wx.ALL, 2)

        # Reset btn
        bmp = self.scaleBmp(wx.Bitmap('rsc/reset.png'), 20, 20)
        btn = wx.BitmapButton(self, -1, bitmap=bmp, size=(bmp.GetWidth()+15, bmp.GetHeight()+15))
        self.Bind(wx.EVT_BUTTON, self.OnResetButton, btn)
        self.HSub.Add(btn, 0, wx.EXPAND|wx.ALL, 2)

        # Save as button
        bmp = self.scaleBmp(wx.Bitmap('rsc/save-as.png'), 20, 20)
        self.SaveButton = wx.BitmapButton(self, -1, bitmap=bmp, size=(bmp.GetWidth()+15, bmp.GetHeight()+15))
        self.SaveButton.Enable(False)
        self.Bind(wx.EVT_BUTTON, self.OnSaveButton, self.SaveButton)
        self.HSub.Add(self.SaveButton, 0, wx.EXPAND|wx.ALL, 2)

        self.wv.SetPage(
        """
        <!DOCTYPE html>
        <html lang="en">
        	<head>
        	<meta charset="utf-8" name="viewport" content="width=device-width, initial-scale=1">
        	<title>SAVi HTML visualisation</title>
        	<style>
        	body {
        		font-family: "Lato", sans-serif;
        	}

        	.sidenav {
        		height: 100%;
        		width: 200px;
        		position: fixed;
        		z-index: 1;
        		top: 0;
        		left: 0;
        		background-color: lightgrey;
        		overflow-x: hidden;
        		padding-top: 20px;
                padding-left: 20px;
        		justify-content: center;
        	}

        	.content {
        		margin-left: 160px; /* Same as the width of the sidenav */
        		font-size: 28px; /* Increased text to enable scrolling */
        		padding: 0px 10px;
        	}

        	@media screen and (max-height: 450px) {
        		.sidenav {padding-top: 15px;}
        		.sidenav a {font-size: 18px;}
        	}
        	</style>
        	</head>
          	<body>
        		<div class="sidenav">
                <h3><b>Blocks information</b></h3>
                <b>Name:</b><div id=Name>-</div>
                <b>Mapping quality:</b><div id=MPQ>-</div>
                <b>Relative strand:</b><div id=REL>-</div>
                <b>Length:</b><div id=LEN>-</div>
                <b>Position on target:</b><div id=POSTAR>-</div>
                <b>Position on query:</b><div id=POSQUE>-</div>
                <b>Queries mapped:</b><div id=QUEMAP>-</div>
                </div>
                <center>
        		<div class=content>
        		<h2><b>SAVi</b> HTML visualisation</h2>
                </div>
                </center>
            </body>
        </html>
        """, "NoneURL")

        self.setCurrentShowcase(self.path + " - {}".format(self.zoom_factor_lst[self.zoom_idx]))

    def OnZoomButton(self, evt) :
        self.zoom_idx += 1
        if self.zoom_idx > len(self.zoom_factor) - 1 :
            self.zoom_idx = len(self.zoom_factor) - 1
        self.wv.SetZoom(self.zoom_factor[self.zoom_idx])
        text = self.path + " - {}".format(self.zoom_factor_lst[self.zoom_idx])
        self.setCurrentShowcase(text)

    def OnDezoomButton(self, evt) :
        self.zoom_idx -= 1
        if self.zoom_idx < 0 :
            self.zoom_idx = 0
        self.wv.SetZoom(self.zoom_factor[self.zoom_idx])
        text = self.path + " - {}".format(self.zoom_factor_lst[self.zoom_idx])
        self.setCurrentShowcase(text)

    def OnResetButton(self, evt) :
        self.zoom_idx = 2
        self.wv.SetZoom(self.zoom_factor[self.zoom_idx])
        text = self.path + " - {}".format(self.zoom_factor_lst[self.zoom_idx])
        self.setCurrentShowcase(text)

    def OnSaveButton(self, evt) :
        # OPENS A DIALOG FOR FILE CHOOSING
        with wx.FileDialog(self, "Save SAVi .HTML file", wildcard="HTML files (*.html)|*.html", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            # IN CASE OF CANCEL FROM USER
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return None
            # GATHERS PATHNAME
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'w') as file:
                    file.write(self.myline)
            except IOError:
                wx.LogError("Cannot save current data in file '%s'." % pathname)

    def setCurrentShowcase(self, text) :
        self.currentSVGshowcase.SetValue("")
        self.currentSVGshowcase.AppendText(text)

    def displaySVG(self, SVGFilePath, target, zoom) :
        f = open(SVGFilePath, "r")
        cat = f.read()
        f.close()

        css = "<style>body {\n\tfont-family: \"Lato\", sans-serif;}\n.sidenav {\n\theight: 100%;\n\twidth: 200px;\n\tposition: fixed;\n\tz-index: 1;\n\ttop: 0;\n\tleft: 0;\n\tbackground-color: lightgrey;\n\toverflow-x: hidden;\n\tpadding-top: 20px;\n\tpadding-left: 20px;\n\tjustify-content: center;}\n.content {\n\tmargin-left: 160px; /* Same as the width of the sidenav */\n\tfont-size: 28px; /* Increased text to enable scrolling */\n\tpadding: 0px 10px;}\n@media screen and (max-height: 450px) {\n\t.sidenav {padding-top: 15px;}\n\t.sidenav a {font-size: 18px;}}</style>"
        head ="<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\" name=\"viewport\" content=\"width=device-width, initial-scale=1\"><title>SAVi HTML visualisation</title>{}</head>".format(css)
        parameters = "<p>Target name: <i>{}</i></p><p>Ratio (px:bp) = <i>1:{}</i></p>".format(target, zoom)
        sidepan ="<div class=\"sidenav\">\n<h3><b>Parameters</b></h3>{}\n<h3><b>Blocks information</b></h3>\n<b>Name:</b><div id=Name>-</div>\n<b>Mapping quality:</b><div id=MPQ>-</div>\n<b>Relative strand:</b><div id=REL>-</div>\n<b>Length:</b><div id=LEN>-</div>\n<b>Position on target:</b><div id=POSTAR>-</div>\n<b>Position on query:</b><div id=POSQUE>-</div>\n<b>Queries mapped:</b><div id=QUEMAP>-</div>\n</div>\n".format(parameters)

        script = "<script>var svg = document.getElementById(\"SVG\");\nsvg.addEventListener(\"click\", click);\nfunction click(e){\nvar string = e.toElement.id;\nvar tabs = string.split(\";\");\nif (tabs.length == 6) {\ndocument.getElementById(\"Name\").innerHTML = tabs[0];\ndocument.getElementById(\"MPQ\").innerHTML = tabs[1];\ndocument.getElementById(\"REL\").innerHTML = tabs[2];\ndocument.getElementById(\"LEN\").innerHTML = tabs[3];\ndocument.getElementById(\"POSTAR\").innerHTML = tabs[4];\ndocument.getElementById(\"POSQUE\").innerHTML = tabs[5];\ndocument.getElementById(\"QUEMAP\").innerHTML = \"Not relevant for this block\";} else if (tabs.length == 3) {\ndocument.getElementById(\"Name\").innerHTML = tabs[0];\ndocument.getElementById(\"LEN\").innerHTML = tabs[1];\ndocument.getElementById(\"MPQ\").innerHTML = \"Not relevant for this block\";\ndocument.getElementById(\"REL\").innerHTML = \"Not relevant for this block\";\ndocument.getElementById(\"POSTAR\").innerHTML = \"Not relevant for this block\";\ndocument.getElementById(\"POSQUE\").innerHTML = \"Not relevant for this block\";\ndocument.getElementById(\"QUEMAP\").innerHTML = tabs[2];} else {\ndocument.getElementById(\"Name\").innerHTML = \"-\";\ndocument.getElementById(\"LEN\").innerHTML = \"-\";\ndocument.getElementById(\"MPQ\").innerHTML = \"-\";\ndocument.getElementById(\"REL\").innerHTML = \"-\";\ndocument.getElementById(\"POSTAR\").innerHTML = \"-\";\ndocument.getElementById(\"POSQUE\").innerHTML = \"-\";\ndocument.getElementById(\"QUEMAP\").innerHTML = \"-\";}}\n</script>"

        body = "<center><div class=content><h2><b>SAVi</b> HTML visualisation</h2>{}</center></div>{}</body></html>".format(cat, script)
        self.myline = head + sidepan + body

        f = open(SVGFilePath + ".html", "w")
        f.write(self.myline)
        f.close()

        self.wv.SetPage(self.myline, "NoneURL")
        self.path = os.path.basename(SVGFilePath)
        text = self.path + " - {}".format(self.zoom_factor_lst[self.zoom_idx])
        self.setCurrentShowcase(text)
        self.SaveButton.Enable(True)

    def scaleBmp(self, bmp, width, height) :
        image = bmp.ConvertToImage()
        image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
        result = wx.Bitmap(image)
        return result
