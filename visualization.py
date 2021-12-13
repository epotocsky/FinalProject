#######
# Calculation and visualtions
#######
import os
import sqlite3
import matplotlib.pyplot as plt

dir_path = os.path.dirname(os.path.realpath(__file__))

def genderScatterPlot(cur, conn):
    # get the data from NetWorth and Artists
    cur.execute("SELECT Artists.name, NetWorth.gender, Artists.fans_count, NetWorth.net_worth FROM NetWorth JOIN Artists ON \
        Artists.artist_id = NetWorth.id WHERE gender != 'NA'")
    data = cur.fetchall()
    colors = ['salmon', 'lightblue']
    fig = plt.figure(figsize = (15, 10))
    for d in data:
        g = 1 if d[1] == 'female' else 0
        x = d[3]/1000000
        y = int(d[2].replace(',', ''))/1000000
        # begin plotting the data
        plt.scatter(x, y, label = d[0], color = colors[g])
        # plt.annotate(text=d[0], xy = (x+0.004, y+0.001), fontsize = 8)

    # customizing a little 
    plt.xlabel('Networth in Million Dollars', fontsize=14)
    plt.ylabel('Number of Fans in Million', fontsize=14)
    plt.title('Gender distributoin in relation to Networth and Number of Fans of Top {} Artists'.format(len(data)), fontsize=14)
    plt.legend(['Female', 'Male'], fontsize = 12)
    # save the plot 
    plt.savefig(dir_path + '/visualizations/gender_Scatter_Plot.png')
    plt.show()
    

def getAvgNetworthByGender(cur):
    # extracting the data 
    cur.execute("SELECT net_worth FROM NetWorth WHERE gender = 'male'")
    male_networth = [x[0] for x in cur.fetchall()]
    cur.execute("SELECT net_worth FROM NetWorth WHERE gender = 'female'")
    female_networth = [x[0] for x in cur.fetchall()]
    # calculate the averages 
    avg_m = sum(male_networth) / len(male_networth) / 1000000
    avg_f = sum(female_networth) / len(female_networth) / 1000000
    # save the data to a file 
    f = open(dir_path + '/calculation_files/avg_networth_by_gender.txt', 'w')
    f.write(f'average networth of male celebrities: {avg_m}, average networth of female celebrities: {avg_f}')
    f.close()
    # plot the data
    plt.bar(['male', 'female'], [avg_m, avg_f], color = ['salmon', 'lightblue'], width = 0.5)
    plt.title('Average networth of celebrities by Gender')
    plt.xlabel("Gender")
    plt.ylabel('Avg Networth in millions')
    # save the plots
    plt.savefig(dir_path + '/visualizations/avg_NetWorth_By_Gender.png')
    plt.show()


def genderFollowersScatterPlot(cur, conn):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    # get the data from Spotify and NetWorth 
    cur.execute("SELECT SpotifyArtistData.name, NetWorth.gender, SpotifyArtistData.followers, TwitterData.follower_count FROM NetWorth JOIN SpotifyArtistData ON SpotifyArtistData.id = NetWorth.id JOIN TwitterData ON TwitterData.id = NetWorth.id WHERE gender != 'NA'")
    data = cur.fetchall()
    colors = ['salmon', 'lightblue']
    fig = plt.figure(figsize = (15, 10))
    for d in data:
        g = 1 if d[1] == 'female' else 0
        x = d[2]/100000
        y = d[3]/100000
        # begin plotting the data
        plt.plot(x, y, 'o', color = colors[g])
    plt.xlabel('Number of Spotify Followers in Hundred-Thousands', fontsize=14)
    plt.ylabel('Number of Twitter Followers in Hundred-Thousands', fontsize=14)
    plt.title('Relationship among Gender and Follower Count', fontsize=14)
    plt.legend(['Female', 'Male'], fontsize = 12)
    
    plt.savefig(dir_path + '/visualizations/gender_Followers_ScatterPlot.png')
    plt.show()

# the following codes are for the 4th visualization 
#Creating a list of genres from the SpotifyGenreData database, so I can iterate through them in my main function.
def createGenrelist(cur, conn):
    cur.execute('SELECT genre_id FROM SpotifyGenreData')
    conn.commit()
    data = cur.fetchall()
    genre_list = []
    genre_list.append(data)
    return genre_list
    
#Creating a list of the names of the genres, so I can use them for my plot x-axis label later
def createGenrelistname(cur, conn):
    cur.execute('SELECT genre FROM SpotifyGenreData')
    conn.commit()
    data = [x[0] for x in cur.fetchall()]
    return data

#Creating my main function to iterate through each genre, get the number of twitter followers for each artist that has the specific genre_id, and then get the average.
# Then I plot the data.
def getTwitterFollowersByGenre(cur, conn): 
    #Calling my function to get the list of genre id's
    genre_id_list = createGenrelist(cur, conn)
    #Creating an empty list to add the average followers to
    avg_list = []
    #Calling the function to get the list of genre id names
    genre_name_list = createGenrelistname(cur, conn)

    # Iterating through the genre_ids to get my follower count data, which is the first item in a tupple.
    for i in genre_id_list[0]:
        cur.execute('SELECT follower_count FROM TwitterData JOIN SpotifyArtistData ON TwitterData.id = SpotifyArtistData.id WHERE SpotifyArtistData.genre_id=?', (i[0],))
        conn.commit()
        rows = cur.fetchall()
        #Creating empty follower list and adding the artists' followers to that for.
        follower_list = []
        follower_list.append(rows)
        count = 0
        artists = 0
        for num in follower_list:
            #Doing this to avoid the divide by zero or any index error, because some genres have 0 twitter followers averages.
            if len(num) == 0:
                pass
            else: 
                count += int(num[0][0])
        #Getting the length of follower list to divide by and get the averages
        artists = len(follower_list)
        average_num = (int(count) / int(artists))
        #Appending my averages to a list, for all of the genres.
        avg_list.append(average_num)
    
        # save the data to a file 
    f = open(dir_path + '/calculation_files/avg_twitter_followers_by_genre.txt', 'w')
    f.write('1. genre, 2. average twitter followers'+ '\n')
    for i in range(len(avg_list)): 
        f.write( f'{genre_name_list[i]}, {avg_list[i]}' + '\n')
    f.close()
    
    #Creating my plot, passing in genre_name_list and avg_list for my axes.
    fig = plt.figure(figsize = (15, 10))
    plt.bar(genre_name_list, avg_list)
    plt.xlabel('Genres', fontsize = 12)
    #Setting accurate labels because there is such a wide range of data, that it has to be (in hundres of millions) for it to all fit into one.
    plt.ylabel('Number of Twitter Followers (in hundreds of millions)', fontsize = 10)  
    plt.title('Avg Number of Twitter Followers per Top Spotify Genre')
    #Rotating my x ticks so they do not get overlapped
    plt.xticks(rotation = 90, fontsize = 7)
    plt.savefig(dir_path + '/visualizations/Avg_Twitter_Followers_Per_Spotify_Genre.png')
    plt.show()


def main():
    conn = sqlite3.connect(dir_path + '/' + "finalproject.db")
    cur = conn.cursor()
    # first visualization  
    genderScatterPlot(cur, conn)
    # second visualization 
    getAvgNetworthByGender(cur)
    # third visualization 
    genderFollowersScatterPlot(cur, conn)
    # fourth visualization 
    getTwitterFollowersByGenre(cur, conn)


if __name__ == "__main__":
    main()
