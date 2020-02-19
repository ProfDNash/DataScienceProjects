import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl
import re
import io
import sqlite3
import time




def gatherData(fhand, year, month):
    info=fhand
    soup = BeautifulSoup(info, 'html.parser')
    articleList = soup('entry')
    for article in articleList:
        idx = str(article('id'))  ##this string needs to be cleaned
        arxiv_id=re.findall("/([0-9,.]+)", idx)
        if len(re.findall("[0-9,.]+", arxiv_id[0]))<1:
            print("Error!  No id!")
        else:
            arxiv_id = re.findall("[0-9,.]+", arxiv_id[0])[0]
        if arxiv_id[0:4] != year+month: continue  ##skip articles with the wrong date
        category = str(article('arxiv:primary_category'))
        category = re.findall('term="([a-z,A-Z,.,-]+)', category)[0]
        if category[0:4] != 'math':continue ##skip non-math classifications
        ##add category data to the database
        cur.execute('INSERT OR IGNORE INTO Classification (subject) VALUES (?)', (category,))
        title = str(article('title'))  ##this string needs to be cleaned
        title = title.replace('[<title>', "").replace('</title>]', "")
        ##add title and arxiv_id to database
        cur.execute('INSERT OR IGNORE INTO Article (id, title, error) VALUES ( ?, ?, 0)', ( "5"+arxiv_id.replace(".",""), title ) )
        ##prepare to add class links
        cur.execute('SELECT id FROM Classification WHERE subject = ? ', (category, ))
        class_id = cur.fetchone()[0]
        cur.execute('INSERT OR IGNORE INTO ClassLinks (article_id, subject_id) VALUES ( ?, ?)', ( "5"+arxiv_id.replace(".",""), class_id ))
        authors = article('author')
        for i in range(len(authors)):
            authors[i] = str(authors[i]('name'))
            authors[i] = authors[i].replace('[<name>', "").replace('</name>]', "")
            ##add author data to the database
            cur.execute('INSERT OR IGNORE INTO Author (name) VALUES (?)', (authors[i],))
            cur.execute('SELECT id FROM Author WHERE name = ? ', (authors[i], ))
            author_id = cur.fetchone()[0]
            cur.execute('INSERT OR IGNORE INTO AuthorLinks (article_id, author_id) VALUES ( ?, ?)', ( "5"+arxiv_id.replace(".",""), author_id ))
        #print("ID:", arxiv_id)
        #print("Title:", title)
        #print("Authors:", authors)
        #print("Category:", category, "\n")
    conn.commit()
    return(len(articleList))
            
def monthByMonth(year,num_results):
    ##error if DropBox is trying to keep up with the updates, so pause syncing first
    for month in ['01','02','03','04','05','06','07','08','09','10','11','12']:
        print(month)
        flag = 0
        start = 0
        while flag==0:
            strt = str(start)
            num = str(num_results)
            #URL = "http://export.arxiv.org/api/query?search_query=math%2F"+ year + month + "*&start=" + strt + "&max_results=" + num
            ##URL changed for post April 2007 format
            URL = 'http://export.arxiv.org/api/query?search_query="'+ year + month + '*"&start=' + strt + "&max_results=" + num
            try:
                fhand = urllib.request.urlopen(URL).read()
            except:
                print("Cannot open initial page.")
                flag=1
            if str(fhand) != "":
                articlesProcessed = gatherData(fhand, year, month)
                if articlesProcessed < num_results:
                    flag = 1
                else:
                    start += num_results
                    print(start)
                    time.sleep(4)
        time.sleep(4)


# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

conn = sqlite3.connect('arXiv.sqlite')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS Article
    (id INTEGER PRIMARY KEY, title TEXT UNIQUE,
     error INTEGER)''')#, old_rank REAL, new_rank REAL)''')

cur.execute('''CREATE TABLE IF NOT EXISTS Classification
    (id INTEGER PRIMARY KEY, subject TEXT UNIQUE)''')

cur.execute('''CREATE TABLE IF NOT EXISTS ClassLinks
    (article_id INTEGER, subject_id INTEGER, PRIMARY KEY (article_id, subject_id))''')

cur.execute('''CREATE TABLE IF NOT EXISTS Author
    (id INTEGER PRIMARY KEY, name TEXT UNIQUE)''')

cur.execute('''CREATE TABLE IF NOT EXISTS AuthorLinks
    (article_id INTEGER, author_id INTEGER, PRIMARY KEY (article_id, author_id))''')

yearList = ['11','12','13','14','15','16','17','18','19','20']
#['92','93','94','95','96','97','98','99','00','01','02','03','04','05','06','07','08','09','10']  ##starting in April 2007, the id number format changed:
num_results = 100
#if 91<int(year)<100:
#            year = "math/"+year
for year in yearList:
    if 91<int(year)<100:
        print("Year: 19"+year)
    else:
        print("Year: 20"+year)
    monthByMonth(year,num_results)

    
