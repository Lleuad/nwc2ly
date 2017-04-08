# -*- coding: utf-8

from __future__ import print_function, unicode_literals
open_old = open
def open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None):
	return open_old(file, mode + ("U" if newline==None else ""), buffering)
