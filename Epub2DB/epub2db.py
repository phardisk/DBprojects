import zipfile
from lxml import etree
import os
import sqlite3

conn = sqlite3.connect('CollClassikdb.sqlite')
cur = conn.cursor()

# Make some fresh tables using executescript()
cur.executescript('''
DROP TABLE IF EXISTS Author;
DROP TABLE IF EXISTS Title;

CREATE TABLE Author (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    author    TEXT UNIQUE
);

CREATE TABLE Title (
    id  INTEGER NOT NULL PRIMARY KEY 
        AUTOINCREMENT UNIQUE,
    title  TEXT,
    author_id  INTEGER,
    year INTEGER, language TEXT, subject TEXT, link TEXT
);
''')

def get_epub_info(book):
    ns = {
        'n': 'urn:oasis:names:tc:opendocument:xmlns:container',
        'pkg': 'http://www.idpf.org/2007/opf',
        'dc': 'http://purl.org/dc/elements/1.1/'
    }

    # prepare to read from the .epub file
    zip = zipfile.ZipFile(filepath+book)

    # find the contents metafile
    txt = zip.read('META-INF/container.xml')
    tree = etree.fromstring(txt)
    cfname = tree.xpath('n:rootfiles/n:rootfile/@full-path', namespaces=ns)[0]

    # grab the metadata block from the contents metafile
    cf = zip.read(cfname)
    tree = etree.fromstring(cf)
    p = tree.xpath('/pkg:package/pkg:metadata', namespaces=ns)[0]

    # repackage the data
    result = {}
    for s in ['title', 'language', 'creator', 'date', 'subject']:
        try:
             result[s] = p.xpath('dc:%s/text()' % (s), namespaces=ns)[0]
        except: continue
    return result


filepath ='dl/Collection classique/'
lstFile = os.listdir(filepath)
for book in lstFile:
        try:
                dict=get_epub_info(book)
                title=str(dict['title'])
                year = int(dict['date'].split('-')[0])
                language=str(dict['language'])
                link=filepath+book
                if 'subject' in dict:
                    subject=str(dict['subject'])
                else:
                    subject ='Not Classified'
                author=dict['creator']

                cur.execute('''INSERT OR IGNORE INTO Author (author) 
                    VALUES ( ? )''', ( author, ) )
                cur.execute('SELECT id FROM Author WHERE author = ? ', (author, ))
                author_id = cur.fetchone()[0]

                cur.execute('''INSERT OR REPLACE INTO Title
                        (title, author_id, year, language,subject,link) 
                        VALUES ( ?, ?, ?, ?,?,?)''',
                        (title, author_id, year, language,subject,link))
        except:
               continue
        conn.commit()

