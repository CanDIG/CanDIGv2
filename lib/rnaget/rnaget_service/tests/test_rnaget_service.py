#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Tests for `candig_rnaget` package."""

import subprocess


def test_dredd():
    subprocess.check_call(['dredd', '--hookfiles=dreddhooks.py'],
                          cwd='./tests')
