#!/usr/bin/env python
# -*- coding: utf-8 -*-
import MySQLdb
import sys
from db import conn_db

cur = conn_db().cursor() 

def get_word(word):
    word = word.strip()
    word_list = []
    cur.execute('SELECT * FROM word WHERE word = "%s"' %(word))
    rows = cur.fetchall()
    for row in rows:
        word_map= {}
        word_map["word"]  = row[0]
        word_map["hash"]  = row[1]
        word_map["ref_word"]  = row[2]
        word_map["part_of_speech"]  = row[3]
        word_map["definition"]  = row[4]
        word_map["examples"]  = row[5]
        word_list.append(word_map)
    return word_list

def reading_train(word_list):
    for i in word_list:
        print i["examples"]
        while True:
            rt = raw_input("Learned? (y/n)").strip()
            if rt in ["y","n"]:
                break            

def spelling_train(word_list):
    pass

def main(argv):
    f = open(argv[0])
    for i in f.readlines():
        word_list = get_word(i)
        if len(word_list) == 0:
            print "Miss %s" % (i)
            continue
        if argv[1] == "read":
            reading_train(word_list)
        elif argv[1] == "spell":
            spelling_train(word_list)
        else:
            pass
            
    return 0

if __name__ == '__main__':
	main(sys.argv[1:])

