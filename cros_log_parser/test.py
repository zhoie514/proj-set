#!/usr/bin/python 
# -*- coding: utf-8 -*-


import datetime

x = "2020-06-08"
y= (datetime.datetime.now()+datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
print(y)