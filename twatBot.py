#!/usr/bin/env python3

import sys
import argparse
import tweepy
#import json
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

    with open('log.txt', 'a') as l:
        l.write(t + "\n")
        
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

def processTweet(tweet, fav, fol, spam):

    op = tweet.user.screen_name
    
    # open file in append mode
    with open('scrapeDump.txt', 'a') as f:
    
        # append poster, time, and tweet to file
        postTime = tweet.created_at.strftime("%Y%b%d %H:%M:%S")
        f.write(postTime +  " @" + op + " ")
        f.write(tweet.text + "\n")
    
    # try to favorite and follow poster if not already
    try:
        # if already spammed post, it'll already be favorited and will throw error so won't double spam
        if fav:
            tweet.favorite()
            log("Favorited @" + op + "'s post")
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


# write file with last x many tweets of interest
def scrapeTwitter(numItems, fav, fol, spam):
    i = 0
   
    # continuously execute mode
    if numItems is 0:
        
        # TODO get tweets for each query
        #tweets = []
        #for i in range(q_length):
             #tweets += tweepy.Cursor(api.search, q=q_lines[i]).items()
        
        # for now just iterate over first query
        try:
            q = tweepy.Cursor(api.search, q=q_lines[0]).items()
        except tweepy.TweepError as e:
            log("TweepyError: " + e.reason)
        
        while True:
            i += 1
            try:
                #for q in tweets:
                tweet = q.next()
                processTweet(tweet, fav, fol, spam)                    
                
            except tweepy.TweepError as e:
                log(i + " tweets scraped")
                log("TweepyError: " + e.reason)
                
                # wait for next request window to continue
                time.sleep(60 * 15)
                continue
            except StopIteration:
                break
                
        log("Scraped: " + str(i) + " tweets with: " + q_lines[0])
                
        
    else: # only iterate over number of tweet specified
    
        for query in q_lines:
            
            for tweet in tweepy.Cursor(api.search, q=query).items(numItems):
                i += 1
                #f.write(json.dumps(tweet._json) + "\n")
                
                processTweet(tweet, fav, fol, spam)
                
            log("Scraped: " + str(i) + " tweets with: " + query)
        
    
# get command line arguments and execute appropriate functions
def main(argv):

    parser = argparse.ArgumentParser(description="Social media promotion bot - Let's get spammy!")

    subparsers = parser.add_subparsers(help='platforms', dest='platform')
    
    # Twitter
    twit_parser = subparsers.add_parser('twitter', help='Scrape twitter for all queries in queries.txt')
    group = twit_parser.add_argument_group('promotion')
    group.add_argument('N', action='store', type=int, help='Num tweets to scrape: N<=200; N=0 when -u | -c')
    group.add_argument('-c', '--continuous', action='store_true', dest='t_con', help='continue executing (within rate limits) until stopped')
    group.add_argument('-a', '--favorite', action='store_true', dest='t_fav', help='favorite matching tweet')
    group.add_argument('-o', '--follow', action='store_true', dest='t_fol', help='follow original tweeter')
    group.add_argument('-r', '--reply', action='store_true', dest='t_rep', help='reply with random promo from promoTweets.txt ')
    twit_parser.add_argument('-u', '--update-status', action='store_true', dest='t_upd', help='update status with random promo from promoTweets.txt ')
    
    # Reddit
    reddit_parser = subparsers.add_parser('reddit', help='Scrape reddit')
    reddit_parser.add_argument('-t', '--test', action='store_true', dest='r_tst', help='help test')

    executed = 0 # catches any command/args that fall through below tree
    args = parser.parse_args()
    
    if args.platform == 'twitter':
        
        # scrape twitter for all queries and favorite, follow, and/or promote OPs
        if args.N > 0:
            scrapeTwitter(args.N, args.t_fav, args.t_fol, args.t_rep)
            executed = 1
        
        # execute continuously, until stopped, while respecting the 900 requests per 15 minutes rate limit
        if args.t_con:
            scrapeTwitter(args.N, args.t_fav, args.t_fol, args.t_rep)
            executed = 1
            
        # update status
        if args.t_upd:
            updateStatus()
            executed = 1
    if args.platform == 'reddit':
        print('yay reddit')
        executed = 1
    
    if not executed:
        print("exit: unknown error")
        parser.print_help()
        sys.exit(1)

            
            
# so main() isn't executed if file is imported
if __name__ == "__main__":
    # remove first script name argument
    main(sys.argv[1:])
    
    
    