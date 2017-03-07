# Import our Twitter credentials from credentials.py
import tweepy
import json
from time import sleep, localtime, strftime
from random import randint
from credentials import *

# get authorization credentials from credentials.py
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

#  load lines (tweets) from text file
my_file = open('tweets.txt', 'r')
file_lines = my_file.readlines()
my_file.close()

# get number of tweets
f_length = sum(1 for _ in file_lines)

def log(s):
    l = open('log.txt', 'a')
    l.write(strftime("%Y%b%d %H:%M:%S", localtime()) + " " + s + "\n")
    l.close()

# tweet line every 20 secs
def tweet():
    # Create a for loop to iterate over file_lines
    for line in file_lines:
        try:
            # skip blank lines
            if line != '\n':
                # send tweet
                api.update_status(line)
                print(strftime("%Y%b%d %H:%M:%S", localtime()) + " Tweeted: " + line)

                # wait 20 seconds between tweets
                sleep(20)
            else:
                pass
        except tweepy.TweepError as e:
            print(e.reason)


# write file with last 100 tweets of interest
def scrapeTwitter():
    # open file in append mode
    f = open('scrapeDump.txt', 'a')
    
    # count number of scraped tweets
    i = 0
    for tweet in tweepy.Cursor(api.search,q='-from:rydercarroll #bulletjournal OR "bullet journal" OR #bujo #android OR android').items(10):
        i = i + 1
        #f.write(json.dumps(tweet._json) + "\n")
        
        op = tweet.user.screen_name
        
        # append poster, time, and tweet to file
        postTime = tweet.created_at.strftime("%Y%b%d %H:%M:%S")
        f.write(op + " - " + postTime + "\n")
        f.write(tweet.text + "\n\n")
        
        # favorite and follow poster if not already
        try:
            # if already spammed post, it'll be favorited and will throw error so won't double spam
            tweet.favorite()
            if not tweet.user.following:
                tweet.user.follow()
                log("Followed: @" + op)
            
            # spam original poster with random promo line
            spam = file_lines[randint(0, f_length - 1)]
            api.update_status('@' + op + ' ' + spam, tweet.id)
            log("Spammed: " + '@' + op)
            
            sleep(5)
        
        except tweepy.TweepError as e:
            log("Error: " + e.reason)
        
    f.close()
    log("Scraped: " + str(i) + " relevant tweets")
    

scrapeTwitter()