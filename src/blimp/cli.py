#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

from .main import Blimp


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("-out", "--outfile", help="set path to output file", action="store", default=None)
    parser.add_argument("-dr", "--dry-run", help="perform a dry run", action="store_true", default=False)
    args = parser.parse_args()

    # run
    Blimp(args).main()
