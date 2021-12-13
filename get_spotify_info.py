#############
# Name: Lizzie Portocsky
# Using the SPOTIFY API to get the popularity information for top 200 artists
# and store the information in the Spotify Info Table
#############
import json
import os
import requests
import sqlite3

client_id = '88d2a36f58ac44b89789ef724bfe42a3'
client_secret = '1edb3b2408b2485ba355482c0960637b'
#get authorization with POST request 
auth_url = 'https://accounts.spotify.com/api/token'
data = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
}
auth_response = requests.post(auth_url, data=data)
#get access token
access_token = auth_response.json().get('access_token')
#print(access_token)

def getLastID(cur, tablename, idname):
    # createa the table
    cur.execute('CREATE TABLE IF NOT EXISTS SpotifyArtistData (id INTEGER PRIMARY KEY, name TEXT, followers INTEGER, genre_id INTEGER)')
    # create another table with shared key 
    cur.execute('CREATE TABLE IF NOT EXISTS SpotifyGenreData (genre_id INTEGER PRIMARY KEY, genre TEXT)')
    # checking what have already been stored to the database
    # get the last row of the database
    # change the table name if expecting to get the id from other tables
    cur.execute('SELECT {} FROM {} ORDER BY {} DESC LIMIT 1'.format(idname, tablename, idname))
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

def getListOfArtists(cur):
    id = getLastID(cur, 'SpotifyArtistData', 'id')
    cur.execute("SELECT artist_id, name FROM Artists WHERE artist_id > ? AND artist_id <= ?", (id, id+20))
    rows = cur.fetchall()
    names = []
    # craete a list of tuples with id as the first element and name as the second element 
    for r in rows: 
        names.append(tuple([r[0], r[1]]))
    #print(names)
    return names

def getArtistInfo(names, cur, conn):
    artist_info= []
    # get the api request url
    for n in names:
        api_url = 'https://api.spotify.com/v1/search?q={}&type=artist&offset=0&limit=1'.format(n[1].lower())
        headers = {'Authorization': 'Bearer {}'.format(access_token)}
        response = requests.get(api_url,headers=headers)
        #check if request was successful
        if response.status_code == requests.codes.ok:
            d = json.loads(response.text)
            artist_info.append(tuple([n[0], n[1], d['artists']['items'][0]['followers']['total'], d['artists']['items'][0]['genres'][0]]))
        else:
            print("Error:", response.status_code, response.text)
    #print(artist_info)
    # store the data into the table
    insertIntoDatabase(artist_info, cur, conn)
    
def insertIntoDatabase(artist_info, cur, conn):
    for t in artist_info:
        # iterate through the list and add them to the table with the id that is the same as the artist_id in the Artists table
        cur.execute('SELECT genre_id FROM SpotifyGenreData WHERE genre = ?', (t[-1],))
        row = cur.fetchone()
        # check if this is the first time inserting any data
        if row: 
            id = row[0]
        else: 
            id = getLastID(cur, 'SpotifyGenreData', 'genre_id') + 1
        print(id)
        
        cur.execute('INSERT OR IGNORE INTO SpotifyArtistData (id, name, followers, genre_id) VALUES (?, ?, ?, ?)', \
                (t[0], t[1], t[2], id) )
        cur.execute('INSERT OR IGNORE INTO SpotifyGenreData (genre_id, genre) VALUES (?, ?)', \
                (id, t[3]) )
    conn.commit()
        

def main():
    # connect to the database
    dir_path = os.path.dirname(os.path.realpath(__file__))
    conn = sqlite3.connect(dir_path + '/' + "finalproject.db")
    cur = conn.cursor()
    artists = getListOfArtists(cur)
    getArtistInfo(artists, cur , conn)


if __name__ == "__main__":
    main()
