#!/usr/bin/python

import os, sys, errno
import re
import urllib2
import logging

from bs4 import BeautifulSoup

from db_tools import PaintDB

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s: %(message)s')

def wget(url):
    return urllib2.urlopen(url).read()

url_template = 'http://francesca-kee.artistwebsites.com/index.html?tab=images&page={0}'

reset_paintings = False
if len(sys.argv) == 2 and sys.argv[1] == "-n":
    reset_paintings = True

pdb = PaintDB(reset_paintings)

images = os.path.join('site', 'images')
thumbnails = os.path.join('site', 'thumbnails')

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

mkdir_p(images)
mkdir_p(thumbnails)


for page in [1, 2, 3]:
    url = url_template.format(page)
    bs = BeautifulSoup(wget(url))

    for t in bs.find_all('div', attrs={'class':'flowdiv'}):
        js = t.div.attrs['onclick']
        link_to_full = re.search('window\.location="?([^"]+)"?', js).group(1)
        logging.debug('found link {0}'.format(link_to_full))
        if not pdb.paint_exists(link_to_full):
            bs_full = BeautifulSoup(wget(link_to_full))
            title = bs_full.find('p', text='Title').parent.find_all('p')[1].text.strip()

            logging.info('processing "{0}", {1}'.format(title, link_to_full))

            thumb_url = t.img['src']
            thumb_file = os.path.join(thumbnails, os.path.basename(thumb_url))
            open(thumb_file, 'w+').write(wget(thumb_url))

            full_url = bs_full.find('img', id='mainimage')['src']
            full_file = os.path.join(images, os.path.basename(full_url))
            open(full_file, 'w+').write(wget(full_url))

            logging.debug("title:{0}, full_img:{1}, thumb_url:{2}".format(title, full_url, thumb_url))
            pdb.add_paint(link_to_full, title, os.path.basename(thumb_url), os.path.basename(full_url))
        else:
            logging.info('Skipping already existing "{0}"'.format(link_to_full))

