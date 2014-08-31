#!/usr/bin/python

import sqlite3, re, os
from jinja2 import Template

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

index_template = Template(open('index.template', 'r').read())
painting_template = Template(open('painting.template', 'r').read())

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
    print info

    row['painting_html'] = re.sub('[^a-zA-Z\d]', '_', row['title'].lower()) + '.html'
    print "generating " + row['painting_html']
    open('site' + os.sep + row['painting_html'], 'w+').write(
            painting_template.render(painting=row, awards=awards, info=info)
            )

open('site' + os.sep + 'index.html', 'w+').write(index_template.render(paintings=rows))

