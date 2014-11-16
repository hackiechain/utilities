#!/usr/bin/env python
# -*- coding: utf-8 -*-
import MySQLdb
import sys,re
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
    
def replace_with_color(text, query_word):
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
    
def reading_train(query_word, word_list):
    for i in word_list:
        print "="*50
        if i["word"] != query_word:
            print add_color(query_word), i["word"], "\t", i["part_of_speech"]
        else:
            print add_color(i["word"]), "\t", i["part_of_speech"]
        print replace_with_color(i["definition"], i["word"]);
        print "-"*50
        print replace_with_color(i["examples"], i["word"]);
        rt = raw_input("").strip()
        
            


def spelling_train(word_list):
    pass

def main(argv):
    f = open(argv[0])
    for i in f.readlines():
        query_word = i.strip()
        word_list = get_word(query_word)
        if len(word_list) == 0:
            print "Miss %s" % (query_word)
            continue
        if argv[1] == "read":
            reading_train(query_word, word_list)
        elif argv[1] == "spell":
            spelling_train(word_list)
        else:
            pass
            
    return 0

if __name__ == '__main__':
	main(sys.argv[1:])

