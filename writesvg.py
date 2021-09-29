#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# General
from templates import *

# Data analysis
import pandas as pd
import numpy as np

def draw_svg_in_memory(data, target) :

    tgt = data.query("tn == @target")

    left = tgt.query("sd == '-'").sort_values(by="al", ascending=False) # Sort by largest aln
    right = tgt.query("sd == '+'").sort_values(by="al", ascending=False) # Sort by largest aln

    print("left:")
    print(left.head())
    print("--------")

    right_columns, right_invisible = define_column(right, right.iloc[0]["tl"])
    left_columns, left_invisible = define_column(left, left.iloc[0]["tl"])

    style_tgt = "stroke:black;stroke-width:2;opacity:0.85"
    style_qry = "stroke:black;stroke-width:1;opacity:0.8"

    # Make target first in position -5 : 5
    strings = []
    no_html_strings = []
    att_string = "name='{}' mq='-' strand='-' qlen='{}' postar='-' posque='-', alen='-'".format(target, tgt.iloc[0]["tl"])
    #                               x      y     w     h
    strings.append(make_rectangle('48%', '0%', '4%', '95%', style_tgt, attstring=att_string, color="red"))
    no_html_strings.append(make_rectangle('48%', '0%', '4%', '95%', style_tgt, attstring="", color="red"))

    # size remaining on right side is 52 to 99% = 47%
    # size remaining on left side is 1% to 48 = 47%
    # find max number of columns
    mx_cl = max([max(right_columns.values()), max(left_columns.values())])
    mx_wh = 47/(2*mx_cl)
    mx_wh = mx_wh if mx_wh < 2 else 2 # set to 2 if mx > 2

    for n, row in right.iterrows() :
        if n in right_invisible :
            continue
        col = right_columns[n]
        pos = 52 + mx_wh * ( 1 + (col * 2) ) # gets the position of rectangle
        # 0 = 0% and length_of_target = 92%
        # So start position "start" is: 5 + (90/tl * ts)
        start = (95/row['tl'])*row['ts']
        # So length is "start - stop" is: ( 5 + (90/tl * te) ) - start
        stop = (95/row['tl'])*row['te']
        length = stop - start
        name, mq, strand, qry_len, alen = row["qn"], row["mq"], "+", row["ql"], row["al"]
        p_on_tgt = str(row["ts"]) + " to " + str(row["te"])
        p_on_qry = str(row["qs"]) + " to " + str(row["qe"])
        att_string = "name='{}' mq='{}' strand='{}' qlen='{}' postar='{}' posque='{}' alen='{}'".format(name, mq, strand, qry_len, p_on_tgt, p_on_qry, alen)
        strings.append(make_rectangle(x=str(pos)+'%', y=str(start)+'%', w=str(mx_wh)+'%', h=str(length)+'%', style=style_qry, attstring=att_string, color="blue"))
        no_html_strings.append(make_rectangle(x=str(pos)+'%', y=str(start)+'%', w=str(mx_wh)+'%', h=str(length)+'%', style=style_qry, attstring="", color="blue"))

    for n, row in left.iterrows() :
        if n in left_invisible :
            continue
        col = left_columns[n]
        pos = 48 - mx_wh * ( 1 + (col * 2) ) - mx_wh # gets the position of rectangle
        start = (95/row['tl'])*row['ts']
        stop = (95/row['tl'])*row['te']
        length = stop - start
        name, mq, strand, qry_len, alen = row["qn"], row["mq"], "-", row["ql"], row["al"]
        p_on_tgt = str(row["ts"]) + " to " + str(row["te"])
        p_on_qry = str(row["qs"]) + " to " + str(row["qe"])
        att_string = "name='{}' mq='{}' strand='{}' qlen='{}' postar='{}' posque='{}' alen='{}'".format(name, mq, strand, qry_len, p_on_tgt, p_on_qry, alen)
        strings.append(make_rectangle(x=str(pos)+'%', y=str(start)+'%', w=str(mx_wh)+'%', h=str(length)+'%', style=style_qry, attstring=att_string, color="blue"))
        no_html_strings.append(make_rectangle(x=str(pos)+'%', y=str(start)+'%', w=str(mx_wh)+'%', h=str(length)+'%', style=style_qry, attstring="", color="blue"))
        
    HTML = MAIN_TEMPLATE_HTML.replace("/* Strings will go here */", "\n".join(l for l in strings))
    SVG = MAIN_TEMPLATE_SVG.replace("/* Strings will go here */", "\n".join(l for l in no_html_strings))

    return HTML, SVG



def define_column(df, tgt_size) :
    """Takes a list of queries and order them in columns to avoid overlaps"""
    columns = [np.zeros(tgt_size)] # create a vector of 0s of tgt_size
    positions = {}
    invisible = []

    for n, row in df.iterrows() :

        s, e = row["ts"], row["te"] # start and stop position of alignment

        # get size proportion of qry compared to target:
        size_prop = (row["al"] / tgt_size)*100
        if size_prop < 0.5 : # if smaller than .5% of target
            invisible.append(n)
            continue

        # min_space between observed queries = 0.5% of tgt_size
        minspace = int(0.005*tgt_size)
        ns = s-minspace if s-minspace > 0 else 0
        ne = e+minspace if e+minspace < tgt_size else tgt_size


        cc = 0
        while True :
            ar = columns[cc] # check next column
            ar[ns:ne] += 1.0
            if np.max(ar) > 1.0 : # then overlap
                if cc+1 == len(columns) : # this means we are in the last column
                    columns.append(np.zeros(tgt_size)) # must create a new column
                    #ar = save_ar.copy() # reset ar
                    ar[ns:ne] -= 1.0
                cc += 1
                continue
            else :
                positions[n] = cc # attribute to row with index 'n' the column 'cc'
                break

    return positions, invisible

def make_rectangle(x, y, w, h, style="", attstring="", color="blue") :
    dc = {'x':x, 'y':y, 'w':w, 'h':h, 's':style, "a":attstring, 'c':color}
    string = "<rect x='{x}' y='{y}' width='{w}' height='{h}' fill='{c}' style='{s}' {a}"
    string += " onmouseover=\"_onhover(evt)\" onmouseout=\"_onout(evt, '" + color + "')\""
    string += "/>"
    string = string.format(**dc)
    return string

#                << attribute("onmouseover", "_onHover(evt)") // Added by AHOUTAIN
#                << attribute("onmouseout", "_onOut(evt, '" + fill.getColorString(layout) + "')") // Added by AHOUTAIN
