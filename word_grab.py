#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2, hashlib, sys
import MySQLdb
from pprint import pprint
from bs4 import BeautifulSoup
from task_runner import TaskRunner, Task
from db import conn_db

def get_uri(word):
    base_uri = 'http://www.collinsdictionary.com/dictionary/american-cobuild-learners/%s'
    return (base_uri % word)

def get_word_content(word):
    headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36' }
    request = urllib2.Request(get_uri(word), None, headers)
    try:
        response = urllib2.urlopen(request)
        page = response.read()
    except Exception as e:
        print e
        page = ""
    return page

def remove_newline(text):
   l = []
   for i in text.splitlines():
       l.append(i.strip())
   return " ".join(l)

def request_word(word):
    word = word.strip()
    if len(word) ==0:
        return None, False
    retry = 3
    while True:
        page = get_word_content(word)
        if not page:
            if retry !=0:
                retry = retry - 1
                continue
            else:
                return None, False
        else:
            break
    pool = BeautifulSoup(page)
    entry = []
    word_found = False
    entry_tag = pool.find_all("div","homograph-entry")
    if not entry_tag:
        return None, word_found
    for per_entry in entry_tag:
        title = per_entry.find("h2","orth").get_text().split(u"\xa0")[0].strip().strip("0123456789. ")
        if word == title.encode('ascii', 'ignore'):
            word_found = True
        explanations_tags = per_entry.find_all("ol","sense_list")
        for i in explanations_tags:
            explanations = []
            exmaples = []
            part_of_speech = i.find_previous_sibling("h4","gramGrp")
            if not part_of_speech:
                continue
            part_of_speech = part_of_speech.find("span","pos").get_text().strip().strip("0123456789. ")
            definition = i.find("span","def").get_text().strip()
            for j in i.find_all("span","orth"):
                if j.find("q"):
                    exmaples.append(remove_newline(j.get_text()))
            explanations.append((part_of_speech, remove_newline(definition), exmaples))
            entry.append((title,explanations))
    return entry, word_found

def write_word_entries(query_word, entry, word_found):
    db = conn_db()
    cur = db.cursor() 
    word = query_word
    if not word_found:
       ref_word = entry[0][0]
       hashchar = hashlib.md5(query_word).hexdigest()
       try:
           cur.execute("INSERT INTO word (hash, word, ref_word) VALUES (%s,%s,%s)", (hashchar, word, ref_word) )
       except MySQLdb.IntegrityError, e:
           print "Dup %s" % (title)
       except MySQLdb.Error, e: 
           print "MySQL Error: %s" % str(e)
           raise

    for i in entry:
        title, explanations = i
        for j in explanations:
            part_of_speech, definition, exmaples = j
            hashchar = hashlib.md5(title.encode('ascii', 'ignore') + definition.encode('ascii', 'ignore')).hexdigest()
            try:
                definition = MySQLdb.escape_string(definition.encode("utf8"))
                exmaples = MySQLdb.escape_string((u"\n".join(exmaples)).encode("utf8"))
                query = u'INSERT INTO word (hash, word, part_of_speech, definition, examples) VALUES ("%s","%s","%s","%s","%s")'  \
							%  (hashchar, title, part_of_speech, definition.decode("utf8"), exmaples.decode("utf8"))
                cur.execute(query)
            except MySQLdb.IntegrityError, e:
                print "Dup %s" % (title)
            except MySQLdb.Error, e:
                print query
                print "MySQL Error: %s" % str(e)
                raise
            except Exception, e:
                print e
                raise
    db.commit()
    cur.close()
    db.close()
 
class WordGrabTask(Task):
    def run(self, obj):
        entry, word_found = request_word(obj)
        if not entry:
            print "No entry %s" %(obj)
            return False
        write_word_entries(obj, entry, word_found)
        print "Done %s" %(obj)
        return True
 
def main(argv):
    f = open(argv[0])
    
    task_runner = TaskRunner(10)
    task_runner.start()
    for i in f.readlines():
        task_runner.add_task(WordGrabTask(i))
    task_runner.join()
	
	
if __name__ == "__main__":
    main(sys.argv[1:])
