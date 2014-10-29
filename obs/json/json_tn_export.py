#!/usr/bin/env python
# -*- coding: utf8 -*-
#
#  Copyright (c) 2014 unfoldingWord
#  http://creativecommons.org/licenses/MIT/
#  See LICENSE file for details.
#
#  Contributors:
#  Jesse Griffin <jesse@distantshores.org>
#
#  Requires PyGithub for unfoldingWord export.

'''
Exports the Key Terms and translationNotes to JSON files.
'''

import os
import re
import sys
import json
import glob
import codecs


root = '/var/www/vhosts/door43.org/httpdocs/data/gitrepo'
pages = os.path.join(root, 'pages')
api = '/var/www/vhosts/api.unfoldingword.org/httpdocs/obs/txt/1/'

# Regexes for grabbing content
ktre = re.compile(ur'====== (.*?) ======', re.UNICODE)
subre = re.compile(ur'\n==== (.*) ====\n', re.UNICODE)
defre = re.compile(ur'===== Definition: =====(.*?)\[See also', re.UNICODE | re.DOTALL)
defre2 = re.compile(ur'===== Definition: =====(.*?)=====', re.UNICODE | re.DOTALL)
factre = re.compile(ur'===== Facts: =====(.*?)\[See also', re.UNICODE | re.DOTALL)
factre2 = re.compile(ur'===== Facts: =====(.*?)=====', re.UNICODE | re.DOTALL)
linknamere = re.compile(ur'\|(.*?)\]\]', re.UNICODE)
cfre = re.compile(ur'See also.*', re.UNICODE)
examplesre = re.compile(ur'===== Examples from the Bible stories.*',
    re.UNICODE | re.DOTALL)
extxtre = re.compile(ur'\*\* (.*)', re.UNICODE)
fridre = re.compile(ur'[0-5][0-9]-[0-9][0-9]', re.UNICODE)

# Regexes for DW to HTML conversion
boldstartre = re.compile(ur'([ ,.])(\*\*)', re.UNICODE)
boldstopre = re.compile(ur'(\*\*)([ ,.])', re.UNICODE)


def getKT(f):
    page = codecs.open(f, 'r', encoding='utf-8').read()
    kt = {}
    kt['term'] = ktre.search(page).group(1).strip()
    kt['sub'] = getKTSub(page)
    kt['def_title'], kt['def'] = getKTDef(page)
    kt['cf'] = getKTCF(page)
    kt['ex'] = getKTExamples(page)
    return kt

def getKTDef(page):
    def_title = 'Definition'
    defse = defre.search(page)
    if not defse:
        defse = defre2.search(page)
    if not defse:
        defse = factre.search(page)
        def_title = 'Facts'
    if not defse:
        defse = factre2.search(page)
        def_title = 'Facts'
    deftxt = defse.group(1).strip()
    return (def_title, getHTML(deftxt))

def getKTSub(page):
    sub = u''
    subse = subre.search(page)
    if subse:
        sub = subse.group(1)
    return sub.strip()

def getKTCF(page):
    cf = []
    cfse = cfre.search(page)
    if cfse:
        text = cfse.group(0)
        cf = linknamere.findall(text)
    return cf

def getKTExamples(page):
    examples = []
    text = examplesre.search(page).group(0)
    for i in text.split('***'):
        ex = {}
        frse = fridre.search(i)
        if not frse:
            continue
        ex['ref'] = frse.group(0)
        ex['text'] = extxtre.search(i).group(1).strip()
        ex['text'] = getHTML(ex['text'])
        examples.append(ex)
    return examples

def getHTML(text):
    # add ul/li
    text = boldstartre.sub(ur'\1<b>', text)
    text = boldstopre.sub(ur'</b>\2', text)
    return text.replace(u'\n', u'<br>')

def writeJSON(outfile, p):
    f = codecs.open(outfile, 'w', encoding='utf-8')
    f.write(getDump(p))
    f.close()

def getDump(j):
    return json.dumps(j, sort_keys=True, indent=2)


if __name__ == '__main__':
    lang = 'en'
    ktpath = os.path.join(pages, lang, 'obs/notes/key-terms')
    apipath = os.path.join(api, lang)
    keyterms = []
    for f in glob.glob('{0}/*.txt'.format(ktpath)):
        if 'home.txt' in f or '1-discussion-topic.txt' in f: continue
        keyterms.append(getKT(f))
    keyterms.sort(key=lambda x: x['term'])
    writeJSON('{0}/kt-{1}.json'.format(apipath, lang), keyterms)
