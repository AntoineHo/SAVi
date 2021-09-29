#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

def read_paf(filepath) :

    print("Reading file...")
    try :
        data = pd.read_csv(
            filepath, sep = "\t", header = None, usecols = range(12),
            names = ["qn", "ql", "qs", "qe", "sd", "tn", "tl", "ts", "te", "nm", "al", "mq"],
            dtype = {"qn":"str", "ql":np.uint64, "qs":np.uint64, "qe":np.uint64, "sd":"category",
                     "tn":"str", "tl":np.uint64, "ts":np.uint64, "te":np.uint64, "nm":np.uint64,
                     "al":np.uint64, "mq":np.uint8},
        )
        return data

    except :
        print("ERROR: Cannot open file or not formatted in .paf")
