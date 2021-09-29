#! /usr/bin/env python3
# -*- coding: utf-8 -*-

MAIN_TEMPLATE_HTML = """
<!DOCTYPE html>
<html lang="en">
    <head>
    <meta charset="utf-8" name="viewport" content="width=device-width, initial-scale=1">
    <title>SAVi HTML visualisation</title>
    <style>
    html {
        height: 100%;
    }
    body {
        font-family: "Lato", sans-serif;
        height: 100%;
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
        margin-left: 200px; /* Same as the width of the sidenav */
        font-size: 28px; /* Increased text to enable scrolling */
        padding: 0px 10px;
    }

    .svg_content {
        height: 100%;
        align: center;
        margin-left: 200px; /* Same as the width of the sidenav */
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
        <b>Aligned length:</b><div id=ALEN>-</div>
        <b>Position on target:</b><div id=POSTAR>-</div>
        <b>Position on query:</b><div id=POSQUE>-</div>
        </div>

        <div class=content>
            <center>
            <h2><b>SAVi</b> HTML visualisation</h2>
            </center>
        </div>
        <div class=svg_content>
            <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="100%" height="95%" id="svg">
                <script type="application/ecmascript">
                  <![CDATA[
                    function _onhover(evt) {
                      var currentRect = evt.target;
                      currentRect.setAttribute("fill", "rgb(0,0,0)");
                      document.getElementById("Name").innerHTML = currentRect.getAttribute("name");
                      document.getElementById("MPQ").innerHTML = currentRect.getAttribute("mq");
                      document.getElementById("REL").innerHTML = currentRect.getAttribute("strand");
                      document.getElementById("LEN").innerHTML = currentRect.getAttribute("qlen");
                      document.getElementById("ALEN").innerHTML = currentRect.getAttribute("alen");
                      document.getElementById("POSQUE").innerHTML = currentRect.getAttribute("posque");
                      document.getElementById("POSTAR").innerHTML = currentRect.getAttribute("postar");
                    }
                    function _onout(evt, color) {
                      var currentRect = evt.target;
                      currentRect.setAttribute("fill", color);
                      document.getElementById("Name").innerHTML = "-";
                      document.getElementById("MPQ").innerHTML = "-";
                      document.getElementById("REL").innerHTML = "-";
                      document.getElementById("LEN").innerHTML = "-";
                      document.getElementById("POSQUE").innerHTML = "-";
                      document.getElementById("POSTAR").innerHTML = "-";
                    }
                  ]]>
                </script>

                /* Strings will go here */

            </svg>
        </div>
    </body>
</html>
"""

MAIN_TEMPLATE_SVG ="""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="100%" height="95%" id="svg">
                <script type="application/ecmascript">
                  <![CDATA[
                    function _onhover(evt) {
                      var currentRect = evt.target;
                      currentRect.setAttribute("fill", "rgb(0,0,0)");
                    }
                    function _onout(evt, color) {
                      var currentRect = evt.target;
                      currentRect.setAttribute("fill", color);
                    }
                  ]]>
                </script>
    /* Strings will go here */

</svg>
"""
