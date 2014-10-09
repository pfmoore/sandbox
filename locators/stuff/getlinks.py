from html.parser import HTMLParser

class LinkScraper(HTMLParser):
    def __init__(self, name):
        HTMLParser.__init__(self)
        self.links = []
        self.href = None
        self.data = None
        self.name = name
        self.internal = False
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for n, v in attrs:
                if n == 'rel':
                    if v == 'internal':
                        self.internal = True
                if n == 'href':
                    self.href = v
    def handle_endtag(self, tag):
        if tag == 'a':
            if self.internal and self.href:
                self.links.append((self.name, self.data, self.href))
            self.data = None
            self.href = None
            self.internal = False
    def handle_data(self, data):
        self.data = data

def scrape_links(name, text):
    parser = LinkScraper(name)
    parser.feed(text)
    return parser.links

from zipfile import ZipFile
import sys, io

all_links = []

zf = ZipFile(sys.argv[1])
for name in zf.namelist():
    with zf.open(name) as f:
        ff = io.TextIOWrapper(f)
        text = ff.read()
        if text:
            links = scrape_links(name, text)
            all_links.extend(links)

import json
with open('links.json', 'w') as f:
    json.dump(all_links, f)
