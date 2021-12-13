#############
# Name: Ember Shan
# This file is to get a list of 200 artists names from the website
# And store them in the Artists table in the database 
# a total of 200 artist names so a total of 10 times executing this code to add all items
#############

import os 
import sqlite3
from bs4 import BeautifulSoup
import requests
import os


def createSoup():
    url = "https://www.songkick.com/leaderboards/popular_artists"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    return soup


def createSoupFromFile():
    # in case the website changes or denied web scraping
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = dir_path + '/backup_website' + 'Most_Popular_Artists_Worldwide.html'
    with open(path) as pg:
        soup = BeautifulSoup(pg, "html.parser")
    return soup


def getLastID(cur):
    # create the table if not exist
    cur.execute('CREATE TABLE IF NOT EXISTS Artists (artist_id INTEGER PRIMARY KEY, name TEXT, fans_count INTEGER)')
    # checking what have already been stored to the database
    # get the last row of the database
    # change the table name if expecting to get the id from other tables
    cur.execute('SELECT artist_id FROM Artists ORDER BY artist_id DESC LIMIT 1')
    row = cur.fetchone()
    # check if this is the first time inserting any data
    if row: 
        # get the id of the last inserted item 
        count = row[0]
        if count == 200: print('All 200 items already inserted')
    else: 
        print('first time inserting the data')
        count = 0 # count for id
    return count


def getData(soup, cur, conn):
    names = []
    fans = []
    start = getLastID(cur)

    table = soup.find('table')
    # check if the data from website is none
    if table != None:
        rows = table.find_all("tr")
        # scraping only 25 elements from the website
        for r in rows[start + 1: start + 21]:
            name_cols = r.find('td', class_ = "name")
            fan = r.find('td', class_ = 'count').text.split()[2]
            names.append(name_cols.text.strip('\n'))
            fans.append(fan)

    # create the artist database 
    createArtistDatabase(cur, conn, names, fans, start)


def createArtistDatabase(cur, conn, names, fans, start):
    # iteraing through the scraped data and insert them into the database
    for i in range(0, len(names)): 
        cur.execute('INSERT OR IGNORE INTO Artists (artist_id, name, fans_count) VALUES (?, ?, ?)', \
            (start+1, names[i], fans[i]))
        start += 1
    conn.commit()


def main():
    # create the soup
    s = createSoup()
    # if cannot scrape from the website, then scrape it form the file
    # s = createSoupFromFile()

    # create the database
    dir_path = os.path.dirname(os.path.realpath(__file__))
    conn = sqlite3.connect(dir_path + '/' + "finalproject.db")
    cur = conn.cursor()

    # get the needed data from the website and create the artists database
    getData(s, cur, conn)
    

if __name__ == "__main__":
    main()