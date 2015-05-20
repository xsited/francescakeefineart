#!/usr/bin/python

import sqlite3, re, os, argparse
from jinja2 import FileSystemLoader, Environment

env = Environment(loader=FileSystemLoader(['.', 'template']))

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--template",
        help="Render specific template as base template",
        default='awards_and_thumbnails.template')
parser.add_argument("-o", "--output",
        help="Where to put rendered base template",
        default=os.path.join('site', 'index.html'))
parser.add_argument("-f", "--faa",
        help="Use original FAA links",
        action="store_true")
args = parser.parse_args()
# http://stackoverflow.com/questions/3300464/how-can-i-get-dict-from-sqlite-query
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

table_name = 'paintings'

con = sqlite3.connect('kee.db')
con.row_factory = dict_factory
c = con.cursor()

c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", [table_name])
if c.fetchone() == None:
    print "Cant find table {0} in sqlite database. Maybe you should run scraping first.".format(table_name)
    exit(-1)

index_template = env.get_template(args.template)
painting_template = env.get_template('painting.template')

c.execute("select rowid,* from {0}".format(table_name))
rows = c.fetchall()

for row in rows:
    c.execute("""
        select description
        from paintings_to_awards
        join awards on paintings_to_awards.a_id = awards.rowid
        where paintings_to_awards.p_id = ?;
        """, [ row['rowid'] ])
    awards = c.fetchall()

    c.execute("""
        select quantity, price, comment
        from misc
        where misc.p_id = ?
        """, [ row['rowid'] ])
    info = c.fetchone()

    if args.faa:
        row['painting_html'] = row['full_url']
    else:
        row['painting_html'] = re.sub('[^a-zA-Z\d]', '_', row['title'].lower()) + '.html'
        print "generating " + row['painting_html']
        open(os.path.join('site', row['painting_html']), 'w+').write(
                painting_template.render(painting=row, awards=awards, info=info)
                )

open(args.output, 'w+').write(index_template.render(paintings=rows))

