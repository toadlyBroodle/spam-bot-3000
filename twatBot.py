#! /usr/bin/env python3

import sys
import argparse
import tweepy
#import json
from time import sleep, localtime, strftime
from random import randint
# Import our Twitter credentials from credentials.py
from credentials import *

# global variables
p_lines = []
p_length = 0
q_lines = []
q_length = 0
api = None


# record certain events in log.txt
def log(s):
    t = strftime("%Y%b%d %H:%M:%S", localtime()) + " " + s

    with open('log.txt', 'a') as l:
        l.write(t + "\n")
        
    # also print truncated log to screen
    p = t[:90] + (t[90:] and '..')
    print(p)


# get authentication credentials and tweepy api object
def authTwitter():

    global p_lines
    global p_length
    global q_lines
    global q_length
    global api

    # get authorization credentials from credentials.py
    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    
    # ensure authentication was successful
    try:
        print("Authenticating...")
        print("Authenticated as: " + api.me().screen_name)
    except tweepy.TweepError as e:
        log("Failed Twitter auth: " + e.reason)
        sys.exit(1)

    #  load promo lines (tweets) from text file
    with open('promoTweets.txt', 'r') as promoFile:
        p_lines = promoFile.readlines()

    # load queries from text file
    with open('queries.txt', 'r') as queryFile:
        q_lines = queryFile.readlines()

    # get number of promotional tweets and queries
    p_length = sum(1 for _ in p_lines)
    q_length = sum(1 for _ in q_lines)


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


def folTweeter(scrn_name):
    try:
        # follow, if not already
        friends = api.get_user(scrn_name).following
        if not friends:
            api.create_friendship(scrn_name)
        else:
            log("Already following: " + scrn_name)
            return
    except tweepy.TweepError as e:
        log("Error: " + e.reason)
        return

    log("Followed: " + scrn_name)


def spamOP(twt_id, scrn_name):
    try:
        # reply to op with random spam
        spamPost = getRandPromo()
        api.update_status('@' + scrn_name + ' ' + spamPost, twt_id)
    except tweepy.TweepError as e:
        log("Error: " + e.reason)
        
    log("Spammed: " + scrn_name)
    # seconds to wait between spam tweets
    sleep(5)


def replyToTweet(twt_id, scrn_name):
    try:
        # favorite tweet, will throw error if tweet already favorited so as to avoid double spamming
        api.create_favorite(twt_id)

        # spam op with random promo line
        spamOP(twt_id, scrn_name)

    except tweepy.TweepError as e:
        log("Error: " + e.reason)
        return

    log("Favorited: " + scrn_name + " [" + twt_id + "]")


def buildDumpLine(tweet):
    return (tweet.created_at.strftime("%b%d %H:%M")
                + "TWT_ID" + str(tweet.id)
                + "SCRN_NAME" + tweet.user.screen_name
                + "TWT_TXT" + tweet.text.replace("\n", "") + "\n")
    
def parseDumpLine(dl):
    # parse scrape dump file, seperate tweet ids from screen names
    a1 = dl.split('TWT_ID')
    a2 = a1[1].split('SCRN_NAME')
    a3 = a2[1].split('TWT_TXT')
    # [time, twt_id, scrn_name, twt_txt]
    return [a1[0], a2[0], a3[0], a3[1]]
   

def processTweet(tweet, pro, fol):

    scrn_name = tweet.user.screen_name
    
    # open dump file in read mode
    with open('scrapeDump.txt', 'r') as f:
        scrp_lines = f.readlines()

        # if tweet already scraped, then return
        if any(str(tweet.id) in s for s in scrp_lines):
            return 0

    # otherwise append to scrapeDump.txt    
    new_line = buildDumpLine(tweet)
    with open('scrapeDump.txt', 'a') as f:
        f.write(new_line)
    
    # follow op, if not already following
    if fol and not tweet.user.following:
        folTweeter(scrn_name)

    # favorite and respond to op's tweet
    if pro:
        replyToTweet(tweet.id, scrn_name)
    
    return 1 # return count of new tweets added to scrapeDump.txt


# continuously scrape for tweets matching all queries
def scrapeTwitter(fol, pro):
   
    def scrape_log(i, k):
        log(("Scraped: {total} tweets ({new} new) found with: {query}\n".format(
        total=str(i), 
        new=str(k), 
        query=query.replace("\n", ""))))
   
    for query in q_lines:
            
        c = tweepy.Cursor(api.search, q=query).items()
        i = 0 # total tweets scraped
        k = 0 # new tweets scraped
        while True:
            try:
                # process next tweet
                k += processTweet(c.next(), pro, fol)                    
                i += 1
            except tweepy.TweepError as e:
                scrape_log(i, k)
                log("Error: " + e.reason)
                
                # wait for next request window to continue
                time.sleep(60 * 15)
                continue
            except StopIteration:
                scrape_log(i, k)
                break
                
                
    
# get command line arguments and execute appropriate functions
def main(argv):

    parser = argparse.ArgumentParser(description="Beep, boop.. I'm a social media promotion bot - Let's get spammy!")

    subparsers = parser.add_subparsers(help='platforms', dest='platform')
    
    # Twitter
    twit_parser = subparsers.add_parser('twitter', help='Scrape twitter for all queries in queries.txt')
    group = twit_parser.add_argument_group('promotion')
    group.add_argument('-s', '--scrape', action='store_true', dest='t_scr', help='scrape for tweets matching query')
    group.add_argument('-f', '--follow', action='store_true', dest='t_fol', help='follow original tweeters in scrapeDump.txt')
    group.add_argument('-p', '--promote', action='store_true', dest='t_pro', help='favorite tweets and reply to tweeters in scrapeDump.txt with random promo from promoTweets.txt')
    twit_parser.add_argument('-u', '--update-status', action='store_true', dest='t_upd', help='update status with random promo from promoTweets.txt ')
    
    # Reddit
    reddit_parser = subparsers.add_parser('reddit', help='Scrape reddit')
    reddit_parser.add_argument('-t', '--test', action='store_true', dest='r_tst', help='help test')

    executed = 0 # catches any command/args that fall through below tree
    args = parser.parse_args()
    
    if args.platform == 'twitter':
        # get authentication credentials and api
        authTwitter()

        # update status
        if args.t_upd:
            updateStatus()
            executed = 1

        # scrape twitter for all queries and favorite, follow, and/or promote OPs
        if args.t_scr:
            scrapeTwitter(args.t_fol, args.t_pro)
            executed = 1
        else: # otherwise promote to all entries in scrapeDump file
            with open('scrapeDump.txt') as f:
                t_lines = f.readlines()

                for t in t_lines:
                    pd = parseDumpLine(t)

                    # ignore lines beginning with '-'
                    if pd[0][0] == '-':
                        continue

                    twt_id = pd[1]
                    scrn_name = pd[2]
                    
                    if args.t_fol:
                        folTweeter(scrn_name)
                    
                    if args.t_pro:
                        replyToTweet(twt_id, scrn_name)
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
    
    
    