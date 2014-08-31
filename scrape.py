#!/usr/bin/python

import os, sys, errno
import re
import urllib2

from bs4 import BeautifulSoup

from db_tools import PaintDB

def wget(url):
    return urllib2.urlopen(url).read()

url_template = 'http://francesca-kee.artistwebsites.com/art/all/francesca+kee+fine+art/all?page={0}'

reset_paintings = False
if len(sys.argv) == 2 and sys.argv[1] == "-n":
    reset_paintings = True

pdb = PaintDB(reset_paintings)

images = 'site' + os.sep + 'images'
thumbnails = 'site' + os.sep + 'thumbnails'

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

mkdir_p(images)
mkdir_p(thumbnails)


for page in [1, 2]:
    url = url_template.format(page)
    bs = BeautifulSoup(wget(url))

    for t in bs.find_all('div', id=re.compile('^artworkdiv')):
        link_to_full = t.div.div.a['href']
        if not pdb.paint_exists(link_to_full):
            bs_full = BeautifulSoup(wget(link_to_full))
            title = bs_full.find('p', text='Title:').next_sibling.string.strip()

            print 'processing "{0}" {1}'.format(title, link_to_full)

            thumb_url = t.div.div.a.img['src']
            thumb_file = thumbnails + os.sep + os.path.basename(thumb_url)
            open(thumb_file, 'w+').write(wget(thumb_url))

            full_url = bs_full.find('img', id='mainimage')['src']
            full_file = images + os.sep + os.path.basename(full_url)
            open(full_file, 'w+').write(wget(full_url))

            #print "title {0}, full img {1}, thumb url {2}".format(title, full_url, thumb_url)
            pdb.add_paint(link_to_full, title, os.path.basename(thumb_url), os.path.basename(full_url))
        else:
            print 'Skipping already existing "{0}"'.format(link_to_full)

