#!/usr/bin/env python
# -*- coding: utf-8 -*-
import MySQLdb

def conn_db():
    return MySQLdb.connect(host="localhost", user="root", passwd="", db="wordbank", charset='utf8')
