import tweepy
import unittest
import sqlite3
import json
import os

consumer_key = "NJGG4V4puH39ZyMiOojs4BBJ5"
consumer_secret = "rS78OXKZucVBlWtOzBIK1M0FoHTkev68LXdM859UK4QYs8xPRb"
access_token = "1383133286629847043-v90SS5wUs90A4SpAcIZDhUzypESi5G"
access_token_secret = "3axQql0Kgmr4hb8pJeAtZsWOK93uShUYW84Jor1fDjduS"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

def getId(cur):
    cur.execute('CREATE TABLE IF NOT EXISTS TwitterData (id INTEGER PRIMARY KEY, name TEXT, screen_name TEXT, follower_count INTEGER)')
    cur.execute('SELECT id FROM TwitterData ORDER BY id DESC LIMIT 1')
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
    id = getId(cur)
    cur.execute("SELECT artist_id, name FROM Artists WHERE artist_id > ? AND artist_id <= ?", (id, id+20))
    rows = cur.fetchall()
    names = []
    # craete a list of tuples with id as the first element and name as the second element 
    for r in rows: 
        names.append(tuple([r[0], r[1]]))
    return names

def getData (name, cur, conn): 
    # path = os.path.dirname(os.path.abspath(__file__))
    # conn = sqlite3.connect(path+'/'+'finalproject.db')
    # cur = conn.cursor()
    # cur.execute('DROP TABLE IF EXISTS TwitterData')
    # cur.execute('CREATE TABLE IF NOT EXISTS TwitterData (id INTEGER PRIMARY KEY, name TEXT, screen_name TEXT, follower_count INTEGER)')

    user_name = None
    screen_name = None
    follower_count = None

    try:
        new_name = name[1].lower().replace(" ", "")
        cursor = tweepy.Cursor(api.user_timeline, id = new_name, tweet_mode = 'extended').items(1)
        print(new_name)
    # follower_count = []
    # screen_name = []
    # names = []
        for i in cursor:
            # print(i)
            verified = i.author.verified
            # print(verified)
            user_name = i.author.name
    # print(i.author.name)
        # names.append(i.author.name)
    # print(i.author.screen_name)
            screen_name = i.author.screen_name
        # screen_name.append(i.author.screen_name)
    # print(i.author.followers_count)
            follower_count = i.author.followers_count
            tweet_count = i.author.statuses_count    
        # follower_count.append(i.author.followers_count)
    except:
        print("Cannot find data for this artist")


    if user_name != None and verified == True:
        print(follower_count)
        # print(user_name)
        # print(screen_name)
        # cur.execute('SELECT artist_id from Artists WHERE name = ?',(user_name,))
        # artist_id = cur.fetchone()[0]
        # print(artist_id)
        # cur.execute('INSERT OR IGNORE INTO TwitterData (id) VALUES (?)', (name[0],))

        cur.execute('INSERT OR IGNORE INTO TwitterData (id, name, screen_name, follower_count) VALUES (?,?,?,?)', (name[0], user_name, screen_name, follower_count))
        conn.commit()



# getData('ladygaga')

def main():
    # connect to the database
    dir_path = os.path.dirname(os.path.realpath(__file__))
    conn = sqlite3.connect(dir_path + '/' + "finalproject.db")
    cur = conn.cursor()
    name_list = getNameList(cur)
    # getData((23, 'ladygaga'), cur, conn)
    for t in name_list:
        getData(t, cur, conn)

if __name__ == "__main__":
    main()


#     for item in i.author:
#         followers = item.followers_count
# print(followers)
# follower_count = []
# for i in cursor:
#     big_data = i.author
#     for item in big_data:
#         follower_count.append(item.followers_count)
# print(follower_count)


# user = api.get_user(screen_name='charli_xcx')


# followers = user.followers_count
# following = user.friends_count
# print("Followers: " + str(followers) + ", " + "Following: " + str(following))

# print(user.screen_name)
# print(user.followers_count)
# for friend in user.friends():
#    print(friend.screen_name)


# def create_table(cur):
#     # first create the table
#     cur.execute('CREATE TABLE IF NOT EXISTS TwitterData (id INTEGER PRIMARY KEY, name TEXT, screen_name TEXT, follower_count INTEGER)')
#     # checking what have already been stored to the database
#     # get the last row of the database
#     # change the table name if expecting to get the id from other tables
#     cur.execute('SELECT id FROM TwitterData ORDER BY id DESC LIMIT 1')
#     row = cur.fetchone()
#     # check if this is the first time inserting any data
#     if row: 
#         # get the id of the last inserted item 
#         count = row[0]
#         if count == 200: print('All 200 items already inserted')
#     else: 
#         print('first time inserting the data')
#         count = 0 # count for id
#     return count


# def getNameList(cur, conn):
#     id = create_table(cur)
#     cur.execute("SELECT artist_id, name FROM Artists WHERE artist_id > ? AND artist_id <= ?", (id, id+20))
#     rows = cur.fetchall()
#     names = []
#     # craete a list of tuples with id as the first element and name as the second element 
#     for r in rows: 
#         names.append(tuple([r[0], r[1]]))
#     conn.commit()
#     return names

# def insertIntoDatabase(follower_count,  cur, conn):
#     # iterate through the list and add them to the table with the id that is the same as the artist_id in the Artists table
#     cur.execute('INSERT OR IGNORE INTO NetWorth (id, name, net_worth, age, gender, nationality) VALUES (?, ?, ?, ?, ?, ?)', \
#                 (t[0], t[1], t[2], t[3], t[4], t[5]) )
#     conn.commit()