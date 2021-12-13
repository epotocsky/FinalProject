#############
# Name: Ember Shan
# Using the tiktok API to get the networth about the artist
# and store the information in the Networth table
# can only find networths for 111 artists out of 200
# need to execute 10 times 
#############
import json
import os
import requests
import sqlite3


def getKey():
    # get my API key from file
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = dir_path + '/' + 'API_keys.txt'
    f = open(path, 'r')
    t = f.readline()
    f.close()
    return t


def getLastID(cur):
    # first create the table
    cur.execute('CREATE TABLE IF NOT EXISTS NetWorth (id INTEGER PRIMARY KEY, name TEXT, net_worth NUMBER, age INTEGER, gender TEXT, nationality TEXT)')
    # checking what have already been stored to the database
    # get the last row of the database
    # change the table name if expecting to get the id from other tables
    cur.execute('SELECT id FROM NetWorth ORDER BY id DESC LIMIT 1')
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


def getNameList(cur):
    id = getLastID(cur)
    cur.execute("SELECT artist_id, name FROM Artists WHERE artist_id > ? AND artist_id <= ?", (id, id+20))
    rows = cur.fetchall()
    names = []
    # craete a list of tuples with id as the first element and name as the second element 
    for r in rows: 
        names.append(tuple([r[0], r[1]]))
    return names


def getNetWorth(names, cur, conn):
    # get the artist infortion from the celebrity API
    key = getKey()
    networth = []
    for n in names:
        # get the api request url
        api_url = 'https://api.api-ninjas.com/v1/celebrity?name={}'.format(n[1].lower())
        r = requests.get(api_url, headers={'X-Api-Key': key} )
        # check if the request succeeded
        if r.status_code == requests.codes.ok:
            d = json.loads(r.text)
            # check if the returned celebrity information is really what we are look for
            for dict in d:
                if dict['name'].lower() == n[1].lower():
                    # create a list of tuples with id, name, networth, age, and gender
                    networth.append(tuple([n[0], n[1], dict.get('net_worth', -1), dict.get('age', -1), dict.get('gender', 'NA'), dict.get('nationality', 'NA')]))
                    break
        else:
            print("Error:", r.status_code, r.text)

    # store the data into the table
    insertIntoDatabase(networth, cur, conn)


def insertIntoDatabase(networth, cur, conn):
    # iterate through the list and add them to the table with the id that is the same as the artist_id in the Artists table
    for t in networth:
        cur.execute('INSERT OR IGNORE INTO NetWorth (id, name, net_worth, age, gender, nationality) VALUES (?, ?, ?, ?, ?, ?)', \
                (t[0], t[1], t[2], t[3], t[4], t[5]) )
    conn.commit()


def main():
    # connect to the database
    dir_path = os.path.dirname(os.path.realpath(__file__))
    conn = sqlite3.connect(dir_path + '/' + "finalproject.db")
    cur = conn.cursor()
    # get the data and insert it into the database
    names = getNameList(cur)
    getNetWorth(names, cur, conn)


if __name__ == "__main__":
    main()