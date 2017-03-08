import sys
import getopt
import tweepy
import json
from time import sleep, localtime, strftime
from random import randint
# Import our Twitter credentials from credentials.py
from credentials import *

# get authorization credentials from credentials.py
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

#  load promo lines (tweets) from text file
promoFile = open('promoTweets.txt', 'r')
p_lines = promoFile.readlines()
promoFile.close()

# load queries from text file
queryFile = open('queries.txt', 'r')
q_lines = queryFile.readlines()
queryFile.close()

# get number of promotional tweets and queries
p_length = sum(1 for _ in p_lines)
q_length = sum(1 for _ in q_lines)


def log(s):
    t = strftime("%Y%b%d %H:%M:%S", localtime()) + " " + s

    l = open('log.txt', 'a')
    l.write(t + "\n")
    l.close()
    # also print truncated log to screen
    p = t[:75] + (t[75:] and '..')
    print(p)


def getRandPromo():
    return p_lines[randint(0, p_length - 1)]


# update status with random promotional tweet
def updateStatus():
    promo = getRandPromo()
    try:
        # skip blank lines
        if promo != '\n':
            # send tweet
            api.update_status(promo)
            log(" Tweeted: " + promo)
    except tweepy.TweepError as e:
        log(e.reason)


# write file with last x many tweets of interest
def scrapeTwitter(query, numItems, fav, fol, spam):
    # open file in append mode
    f = open('scrapeDump.txt', 'a')
    
    # count number of scraped tweets
    i = 0
    for tweet in tweepy.Cursor(api.search, q = query).items(numItems):
        i = i + 1
        #f.write(json.dumps(tweet._json) + "\n")
        
        op = tweet.user.screen_name
        
        # append poster, time, and tweet to file
        postTime = tweet.created_at.strftime("%Y%b%d %H:%M:%S")
        f.write(op + " - " + postTime + "\n")
        f.write(tweet.text + "\n\n")
        
        # favorite and follow poster if not already
        try:
            # if already spammed post, it'll already be favorited and will throw error so won't double spam
            if fav:
                tweet.favorite()
            if fol and not tweet.user.following:
                tweet.user.follow()
                log("Followed: @" + op)
            
            # spam original poster with random promo line
            if spam:
                spamPost = getRandPromo()
                api.update_status('@' + op + ' ' + spamPost, tweet.id)
                log("Spammed: " + '@' + op)
                # seconds to wait between spam tweets
                sleep(5)
        
        except tweepy.TweepError as e:
            log("Error: " + e.reason)
        
    f.close()
    log("Scraped: " + str(i) + " tweets with: " + query)

def usage():
    print("usage: " + sys.argv[0] + " [-s,--scrape-twitter <n> [-a,--favorite] [-o,--follow] [-p,--promote]] [-u,--update-status] [-h,--help]\n\twhere <n> is number of tweets to scrape (n<=200)")

# get command line arguments and execute appropriate functions
def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hs:uaop", ["help", "update-status", "scrape-twitter=", "favorite", "follow", "promote"])
    except getopt.GetoptError:
          usage()
          sys.exit(2)
    if len(opts) == 0:
        usage()
        sys.exit()

    scrape = 0
    count = 0
    update = 0
    favorite = 0
    follow = 0
    promote = 0

    # get argument flags
    for opt, arg in opts:
        if opt in ("-s", "--scrape-twitter"):
            scrape = 1
            count = int(arg)
        if opt in ("-a", "--favorite"):
            favorite = 1
        if opt in ("-o", "--follow"):
            follow = 1
        if opt in ("-p", "--promote"):
            promote = 1
        if opt in ("-u", "--update-status"):
            update = 1
        # display usage help
        if opt in ("-h", "--help"):
            usage()
            sys.exit()

    # scrape twitter for all queries and favorite, follow, and/or promote OPs
    if scrape:
        for query in q_lines:
            scrapeTwitter(query, count, favorite, follow, promote)
    # update status
    if update:
        updateStatus()


if __name__ == "__main__":
    # remove first script name argument
    main(sys.argv[1:])