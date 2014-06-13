"""Generates a Dash Docset for Google's Closure JavaScript library.

Requires BeautifulSoup4.

For automated setup & build, see ./Makefile and scripts referenced thereof.
If you enjoy typing in shell commands manually, or if you're on a platform where
the scripts don't work, instructions are below.

Generate the latest docset:
  # Make sure you've pulled the Closure submodule's contents (see
  # ./.gitmodules), then:
  cp Info.plist goog.docset/Contents/.
  cp goog.docset/Contents/Resources/Documents/static/images/16px.png goog.docset/icon.png
  curl -o bs4.tgz http://www.crummy.com/software/BeautifulSoup/bs4/download/4.2/beautifulsoup4-4.2.0.tar.gz
  tar -xzf bs4.tgz
  cp -r beautifulsoup4-4.2.0/bs4 .
  python gendocset.py
  open goog.docset
Package a generated docset:
  tar --exclude='.DS_Store' --exclude='.git' -czf docset.tgz goog.docset

"""
import bs4
import glob
import os
import re
import sqlite3
from os import path

# The online documentation's JavaScript causes the anchors to be worthless.
# Loading a page with an anchor will not go to the correct spot because the
# elements are by default expanded and the nav will happen before they get
# collapsed. Sadly, you must use a local copy where the JS is not enabled.
USE_ONLINE_DOCS = False

if USE_ONLINE_DOCS:
  ONLINE_DOC_PATH = 'http://google.github.io/closure-library/api/'
else:
  ONLINE_DOC_PATH = ''


class DocSet(object):
  CREATE_TBL = 'CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);'
  CREATE_IDX = 'CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);'
  DROP_TBL = 'DROP TABLE searchIndex;'
  INSERT = 'INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)'
  DOCSET_SQLLITE = 'goog.docset/Contents/Resources/docSet.dsidx'

  def __init__(self):
    self.db = None
    self.format_doc_path = lambda path: path

  def connect(self):
    if self.db: return
    self.db = sqlite3.connect(self.DOCSET_SQLLITE)
    self.cur = self.db.cursor()

  def clear(self):
    self.connect()
    try: self.cur.execute(self.DROP_TBL)
    except: pass
    self.cur.execute(self.CREATE_TBL)
    self.cur.execute(self.CREATE_IDX)

  def disconnect(self):
    if not self.db: return
    self.db.commit()
    self.db.close()
    self.db = None

  def __enter__(self):
    self.clear()
    return self

  def __exit__(self, type, value, tb):
    self.disconnect()

  def _add(self, name, doc_path, doc_type='Function'):
    print '%s %s:\n\t%s' %(doc_type.upper(), name, doc_path)
    self.cur.execute(self.INSERT,
                     (name,
                      doc_type,
                      ONLINE_DOC_PATH + self.format_doc_path(doc_path)))

  def add_const(self, name, path):
    self._add(name, path, doc_type='Const')

  def add_method(self, name, path):
    self._add(name, path, doc_type='Method')

  def add_class(self, name, path):
    self._add(name, path, doc_type='Class')

  def add_fn(self, name, path):
    self._add(name, path)


class ClosureDocs(object):

  DOCPATH = 'goog.docset/Contents/Resources/Documents/api/*'
  METHOD_PATTERN = re.compile('(.*\.?\w+)\.prototype\.(\w+)')
  CONST_PATTERN = re.compile('.*\.[A-Z_]+$')

  def __init__(self, docset):
    self.docset = docset
    self.docset.format_doc_path = lambda path: 'api/' + path

  def find_classes(self, soup, unused_file_name):
    classes = soup.select('div.fn-constructor a')
    for cls in classes:
      name = cls.contents[0].strip()
      doc_path = cls.attrs['href']
      self.docset.add_class(name, doc_path)

  def find_functions(self, soup, file_name):
    functions = soup.select('.entry.public a[name]')
    for function in functions:
      full_namespace = function.attrs['name']
      doc_path = '%s#%s' % (file_name, full_namespace)
      name = full_namespace
      doc_type = 'Function'

      method = self.METHOD_PATTERN.search(full_namespace)
      const = self.CONST_PATTERN.search(full_namespace)
      if method:
        doc_type = 'Method'
        name = '%s.%s' % (method.group(1), method.group(2))
        self.docset.add_method(name, doc_path)
      elif const:
        doc_type = 'Const'
        self.docset.add_const(name, doc_path)
      else:
        self.docset.add_fn(name, doc_path)

  def parse_soup(self, soup, file_name):
    self.find_classes(soup, file_name)
    self.find_functions(soup, file_name)

  def parse(self):
    for path in glob.glob(self.DOCPATH):

      if os.path.isdir(path): continue
      with open(path) as doc:
        file_name = os.path.basename(path)
        print 'Processing %s' % file_name
        soup = bs4.BeautifulSoup(doc, 'lxml')
        self.parse_soup(soup, file_name)


with DocSet() as docset:
  ClosureDocs(docset).parse()



