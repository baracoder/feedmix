#!/usr/bin/env python

from multiprocessing.pool import ThreadPool

from time import mktime
from functools import reduce

import os

import feedparser

from flask import Flask, render_template
from flask_cache import Cache


app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Stuff to go at the top of the feed.
name = os.getenv('RSS_TITLE')
description = os.getenv('RSS_DESCRIPTION')
link = os.getenv('RSS_LINK')
feed_url = os.getenv('RSS_URL')
feeds = os.getenv('RSS_FEEDS').split('|')



@app.route('/')
@cache.cached(timeout=300)
def main():
    pool = ThreadPool()
    feed_objects = pool.map(feedparser.parse, feeds)
    entries = reduce(lambda l, f: l + f.entries, feed_objects, [])
    entries.sort(key=lambda e: mktime(e.updated_parsed), reverse=True)
    return render_template('feed.xml', name=name, description=description,
                           link=link, feed_url=feed_url, items=entries), 200, {'Content-Type': 'application/rss+xml; charset=utf-8'}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='80')
