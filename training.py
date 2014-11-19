#!/usr/bin/env python
# -*- coding: utf-8 -*-
import MySQLdb
import sys,re
from db import conn_db
conn = conn_db()
cur = conn.cursor() 

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
        word_map["commonness"]  = row[6]
        word_map["pron"]  = row[7]
        if word_map["ref_word"] != None:
            ref_list = get_word(word_map["ref_word"])
            word_list = word_list + ref_list
        else:
            word_list.append(word_map)
    return word_list

def add_color(word):
    '''
    print '\033[1;30mGray like Ghost\033[1;m'
    print '\033[1;31mRed like Radish\033[1;m'
    print '\033[1;32mGreen like Grass\033[1;m'
    print '\033[1;33mYellow like Yolk\033[1;m'
    print '\033[1;34mBlue like Blood\033[1;m'
    print '\033[1;35mMagenta like Mimosa\033[1;m'
    print '\033[1;36mCyan like Caribbean\033[1;m'
    print '\033[1;37mWhite like Whipped Cream\033[1;m'
    print '\033[1;38mCrimson like Chianti\033[1;m'
    print '\033[1;41mHighlighted Red like Radish\033[1;m'
    print '\033[1;42mHighlighted Green like Grass\033[1;m'
    print '\033[1;43mHighlighted Brown like Bear\033[1;m'
    print '\033[1;44mHighlighted Blue like Blood\033[1;m'
    print '\033[1;45mHighlighted Magenta like Mimosa\033[1;m'
    print '\033[1;46mHighlighted Cyan like Caribbean\033[1;m'
    print '\033[1;47mHighlighted Gray like Ghost\033[1;m'
    print '\033[1;48mHighlighted Crimson like Chianti\033[1;m'
    '''    
    
    return "\033[1;32m"+word+"\033[1;m"
    
def replace_with_color(text, query_word=None):
    if query_word == None:
        query_word = text
    def matchcase(word):
        def replace(m):
            text = m.group()
            if text.isupper():
                return add_color(word.upper())
            elif text.islower():
                return add_color(word.lower())
            elif text[0].isupper():
                return add_color(word.capitalize())
            else:
                return add_color(word)
        return replace
    return re.sub(query_word, matchcase(query_word), text, flags=re.IGNORECASE)
    
def replace_with_blank(text, query_word=None):
    if query_word == None:
        query_word = text
    def matchcase(word):
        def replace(m):
            return len(word)*"_"
        return replace    
    return re.sub(query_word, matchcase(query_word), text, flags=re.IGNORECASE)
    
def show_word(query_word, i, replace_func):
    if i["word"] != query_word:
        print replace_func(query_word), replace_func(i["word"]), "\t", replace_func(i["pron"]), i["part_of_speech"],i["commonness"]
    else:
        print replace_func(i["word"]), "\t", replace_func(i["pron"]), i["part_of_speech"],i["commonness"]
    print replace_func(i["definition"], i["word"])
    print "-"*50
    print replace_func(i["examples"], i["word"])
    
def recall_train(query_word, entry_list, recall_level):
    recall_level = int(recall_level)
    for i in entry_list:
        cur.execute('SELECT * FROM memory WHERE hash = "%s"' %(i["hash"]))
        rt = cur.fetchone()
        if rt == None:
            continue
        if rt[2] != recall_level:
            continue
        print "="*50
        show_word(query_word, i, replace_with_blank)
        while True:
            rt = raw_input("remember? (y/n/r)").strip()
            if rt in ["y","n"]:
                break
            if rt == "r":
                print add_color(i["word"]), i["pron"]
        if rt == "y":
            reading_value = recall_level + 1
        else:
            if recall_level > 0:
                reading_value = recall_level -1
            else:
                reading_value = recall_level
        print add_color(i["word"]), i["pron"]
        query = 'INSERT INTO memory (hash, reading) VALUES ("%s", %s) ON DUPLICATE KEY UPDATE reading = %s' % (i["hash"], reading_value, reading_value)
        cur.execute(query)
    conn.commit()
    
def reading_all(query_word, entry_list):
    for i in entry_list:
        cur.execute('SELECT * FROM memory WHERE hash = "%s"' %(i["hash"]))
        rt = cur.fetchone()
        if rt != None:
            continue
        print "="*50
        show_word(query_word, i, replace_with_color)
        while True:
            rt = raw_input("new? (y/n)").strip()
            if rt in ["y","n"]:
                break
        if rt == "y":
            reading_value = 0
        else:
            reading_value = 1
        query = 'INSERT INTO memory (hash, reading) VALUES ("%s", %s) ON DUPLICATE KEY UPDATE reading = %s' % (i["hash"], reading_value, reading_value)
        cur.execute(query)
    conn.commit()

def spelling_train(query_word, entry_list):
    pass

def main(argv):
    with open(argv[0]) as myfile:
        total = sum(1 for line in myfile if line.rstrip('\n'))
    f = open(argv[0])
    count = 0
    for i in f.readlines():
        count = count +1
        query_word = i.strip()
        entry_list = get_word(query_word)
        if len(entry_list) == 0:
            print "Miss %s" % (query_word)
            continue
        if argv[1] == "read":
            reading_all(query_word, entry_list)
        elif argv[1] == "recall":
            recall_train(query_word, entry_list, argv[2])            
        elif argv[1] == "spell":
            spelling_train(query_word, entry_list)
        else:
            pass
        print "Progress: %s/%s" % (count,total)
    return 0
    
if __name__ == '__main__':
	main(sys.argv[1:])

