# -*- coding: utf-8 -*-
import urllib2
from pprint import pprint
from bs4 import BeautifulSoup
def get_uri(word):
    base_uri = 'http://www.collinsdictionary.com/dictionary/american-cobuild-learners/%s'
    return (base_uri % word)

def get_word_content(word):
    headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36' }
    request = urllib2.Request(get_uri(word), None, headers)
    try:
        response = urllib2.urlopen(request)
        the_page = response.read()
    except Exception as e:
        the_page = ""
    return the_page

def remove_newline(text):
   l = []
   for i in text.splitlines():
       l.append(i.strip())
   return " ".join(l)

def request_word(word):
    page = get_word_content(word)
    if not page:
        return None
    pool = BeautifulSoup(page)
    entry_tag = pool.find("div","homograph-entry").find("h2","orth").get_text()
    title = entry_tag.split(u"\xa0")[0]

    explanations = []
    exmaples = []
    explanations_tags = pool.find_all("ol","sense_list")
    for i in explanations_tags:
        part_of_speech = i.find_previous_sibling("h4","gramGrp").find("span","pos").get_text().split()[-1]
        definition = i.find("span","def").get_text()
        explanations.append((part_of_speech, remove_newline(definition)))
        for j in i.find_all("span","orth"):
            exmaples.append(remove_newline(j.get_text()))

    print "\n\n\n"
    pprint(title)
    pprint(explanations)
    pprint(exmaples)


 

request_word("test")
request_word("arrogance")
