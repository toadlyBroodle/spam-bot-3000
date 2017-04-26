#! /usr/bin/env python3

import sys
import signal
import argparse
import pprint
import json
from time import sleep, localtime, strftime
import datetime
from random import randint
# Reddit imports:
import praw
import pdb
import re
import os
# Twitter imports: credentials from credentials.py
import tweepy
from credentials import *

# global variables
# twitter
p_lines = []
p_length = 0
q_lines = []
q_length = 0
api = None
# reddit
reddit = None
reddit_subkeys = None


# record certain events in log.txt
def log(s):
    t = strftime("%Y%b%d %H:%M:%S", localtime()) + " " + s

    with open('log.txt', 'a') as l:
        l.write(t + "\n")
        
    # also print truncated log to screen
    p = t[:90] + (t[90:] and '..')
    print(p)

def authReddit():
    global reddit
    global reddit_subkeys

    print("Authenticating...")

    reddit = praw.Reddit('twatBot')

    log("Authenticated as: " + str(reddit.user.me()));

    # get subreddits, e.g.: androidapps+androiddev+all
    with open('red_subkey_pairs.json') as json_data:
        subkeys_parsed = json.load(json_data)
        reddit_subkeys = subkeys_parsed['sub_key_pairs']

def buildRedDumpLine(submission):
    return (datetime.datetime.fromtimestamp(int(submission.created)).strftime("%b%d %H:%M")
            + "SUBM_URL" + str(submission.url)
            + "SUBM_TXT" + submission.selftext.replace("\n", "") + "\n")

def parseRedDumpLine(dl):
    # parse scrape dump file, seperate tweet ids from screen names
    a1 = dl.split('SUBM_URL')
    a2 = a1[1].split('SUBM_TXT')
    # [time, twt_id, scrn_name, twt_txt]
    return [a1[0], a2[0], a2[1]]

def processSubmission(submission):
    # open dump file in read mode
    with open('red_scrape_dump.txt', 'r') as f:
        scrp_lines = f.readlines()

        # if submission already scraped, then return
        if any(str(submission.id) in s for s in scrp_lines):
            return 0

    # otherwise append to red_scrape_dump.txt
    with open('red_scrape_dump.txt', 'a') as f:
        f.write(buildRedDumpLine(submission))
        return 1

def getRandRedPromo():
    with open('red_promos.txt') as f:
        rp_lines = f.readlines()
        f_length = sum(1 for _ in rp_lines)
        return rp_lines[randint(0, f_length - 1)]
        
def replyReddit():
     # open dump file in read mode
    with open('red_scrape_dump.txt', 'r') as f:
        post_lines = f.readlines()

        # reply to lines not marked with prefix '-'
        for post in post_lines:
            pd = parseRedDumpLine(post)

            if pd[0][0] == '-':
                continue
            # get submission from submission.id stored in scrape dump
            submission = reddit.submission(url=pd[1])
            # reply with random promotion
            try:
                submission.reply(getRandRedPromo())
                log('Replied: ' + pd[1])
                
                # wait for 45-75 secs to evade spamming flags
                sleep(randint(45, 75))
            except praw.exceptions.ClientException as e:
                log("Error: " + e.message)

def scrapeReddit(scrape_limit, r_new, r_top, r_hot, r_ris):
    
    def scrape_log(i, k):
        log("Scraped: {total} submissions ({new} new) in {subs}".format(
            total=str(i), 
            new=str(k),
            subs=subredstr))

    # search each subreddit combo for new submissions matching its associated keywords
    for subkey in reddit_subkeys:
        i = 0 # total submissions scraped
        k = 0 # new submissions scraped
        
        subredstr = subkey["subreddits"]
        subreddits = reddit.subreddit(subredstr)
        
        # search new, hot, or rising categories?
        category = None
        if r_new:
            category = subreddits.new(limit=int(scrape_limit))
            print("Searching new " + str(subreddits))
        elif r_top:
            category = subreddits.top(limit=int(scrape_limit))
            print("Searching top " + str(subreddits))
        elif r_hot:
            category = subreddits.hot(limit=int(scrape_limit))
            print("Searching hot " + str(subreddits))
        elif r_ris:
            category = subreddits.rising(limit=int(scrape_limit))
            print("Searching rising " + str(subreddits))
        else:
            print("Which category would you like to scrape? [-n|-t|-H|-r]")
            sys.exit(1)
        
        # indefinitely monitor new submissions with: subreddit.stream.submissions()
        for submission in category:
            done = False
            # process any submission with title/text fitting and/or/not keywords
            tit_txt = submission.title.lower() + submission.selftext.lower()

            # must not contain any NOT keywords
            for kw in subkey['keywords_not']:
                if kw in tit_txt:
                    done = True
            if done:
                continue

            # must contain all AND keywords
            for kw in subkey['keywords_and']:
                if not kw in tit_txt:
                    done = True
            if done:
                continue

            # must contain at least one OR keyword
            for kw in subkey['keywords_or']:
                if kw in tit_txt:
                    break

            k += processSubmission(submission)
            i += 1                    
        scrape_log(i, k)


# get authentication credentials and tweepy api object
def authTwitter():

    global p_lines
    global p_length
    global q_lines
    global q_length
    global api

    # get authorization credentials from credentials.py
    print("Authenticating...")
    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    
    # ensure authentication was successful
    try:
        log("Authenticated as: " + api.me().screen_name)
    except tweepy.TweepError as e:
        log("Failed Twitter auth: " + e.reason)
        sys.exit(1)

    #  load promo lines (tweets) from text file
    with open('twit_promos.txt', 'r') as promoFile:
        p_lines = promoFile.readlines()

    # load queries from text file
    with open('twit_queries.txt', 'r') as queryFile:
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
    # reply to op with random spam
    spamPost = getRandPromo()
    api.update_status('@' + scrn_name + ' ' + spamPost, twt_id)

    log("Spammed: " + scrn_name)
    
    # wait 45-75 seconds between spam tweets
    wt = randint(45, 75)
    print("waiting " + str(wt) + "s...")
    sleep(wt)


def replyToTweet(twt_id, scrn_name):
    try:
        # favorite tweet, will throw error if tweet already favorited so as to avoid double spamming
        api.create_favorite(twt_id)

        # try spamming op with random promo line
        spamOP(twt_id, scrn_name)

        log("Favorited: " + scrn_name + " [" + twt_id + "]")
        return 1
            
    except tweepy.TweepError as e:
        if '139' in e.reason:
            log("Already favorited/spammed " + scrn_name + ": " + e.reason)
            return 0
        elif '226' in e.reason:
            log(e.reason)
            log("Automated activity detected: waiting for next 15m window...")
            # wait for next 15m window to throw anti-spam bots off the scent
            sleep(randint(900, 1000))
            return 2
        else:
            log(e.reason)
            log("Terminal API Error returned: exiting, see log.txt for details.")
            return 3

def directMessageTweet(scrn_name):
    try:
        # send direct message to tweeter
        api.send_direct_message(screen_name=scrn_name, text=getRandPromo())

    except tweepy.TweepError as e:
        log("Error: " + e.reason)
        return
    
    log("Direct Messaged: " + scrn_name)
    
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
   

def processTweet(tweet, pro, fol, dm):

    scrn_name = tweet.user.screen_name
    
    # open dump file in read mode
    with open('twit_scrape_dump.txt', 'r') as f:
        scrp_lines = f.readlines()

        # if tweet already scraped, then return
        if any(str(tweet.id) in s for s in scrp_lines):
            return 0

    # otherwise append to twit_scrape_dump.txt    
    new_line = buildDumpLine(tweet)
    with open('twit_scrape_dump.txt', 'a') as f:
        f.write(new_line)
    
    # follow op, if not already following
    if fol and not tweet.user.following:
        folTweeter(scrn_name)

    # favorite and respond to op's tweet
    if pro:
        replyToTweet(tweet.id, scrn_name)
        
    # direct message op
    if dm:
        directMessageTweet(scrn_name)
    
    return 1 # return count of new tweets added to twit_scrape_dump.txt


# continuously scrape for tweets matching all queries
def scrapeTwitter(con, eng, fol, pro, dm):
   
    def scrape_log(i, k):
        log(("Scraped: {total} tweets ({new} new) found with: {query}\n".format(
        total=str(i), 
        new=str(k), 
        query=query.replace("\n", ""))))
   
    for query in q_lines:
        c = None
        if eng:
            c = tweepy.Cursor(api.search, q=query, lang='en').items()
        else:
            c = tweepy.Cursor(api.search, q=query).items()
        i = 0 # total tweets scraped
        k = 0 # new tweets scraped
        while True:
            try:
                # prompt user to continue scraping after 50 results
                if (not con and i%51 == 50):
                    query_trunc = query[:20] + (query[20:] and '..')
                    keep_going = input("{num} results scraped for {srch}, keep going? (Y/n):".format(num=str(i), srch=query_trunc))
                    if (keep_going != "Y"):
                        raise StopIteration()
                # process next tweet
                k += processTweet(c.next(), pro, fol, dm)                    
                i += 1
            except tweepy.TweepError as e:
                if '403' in e.reason:
                    log("403 not found: check your queries for validity")
                    sys.exit(1)
                scrape_log(i, k)
                log("Reached API window limit: taking 15min smoke break..." + e.reason)
                # wait for next request window to continue
                sleep(60 * 15)
                continue
            except StopIteration:
                scrape_log(i, k)
                break


# get command line arguments and execute appropriate functions
def main(argv):

    # catch SIGINTs and KeyboardInterrupts
    def signal_handler(signal, frame):
            log("Current job terminated: received KeyboardInterrupt kill signal.")
            sys.exit(0)
    # set SIGNINT listener to catch kill signals
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description="Beep, boop.. I'm a social media promotion bot - Let's get spammy!")

    subparsers = parser.add_subparsers(help='platforms', dest='platform')
    
    # Twitter arguments
    twit_parser = subparsers.add_parser('twitter', help='Twitter: scrape for queries, promote to results')
    twit_parser.add_argument('-u', '--update-status', action='store_true', dest='t_upd', help='update status with random promo from twit_promos.txt ')
    group_scrape = twit_parser.add_argument_group('query')
    group_scrape.add_argument('-s', '--scrape', action='store_true', dest='t_scr', help='scrape for tweets matching queries in twit_queries.txt')
    group_scrape.add_argument('-c', '--continuous', action='store_true', dest='t_con', help='scape continuously - suppress prompt to continue after 50 results per query')
    group_scrape.add_argument('-e', '--english', action='store_true', dest='t_eng', help='return only tweets written in English')
    
    group_promote = twit_parser.add_argument_group('spam')
    group_promote.add_argument('-f', '--follow', action='store_true', dest='t_fol', help='follow original tweeters in twit_scrape_dump.txt')
    group_promote.add_argument('-p', '--promote', action='store_true', dest='t_pro', help='favorite tweets and reply to tweeters in twit_scrape_dump.txt with random promo from twit_promos.txt')
    group_promote.add_argument('-d', '--direct-message', action='store_true', dest='t_dm', help='direct message tweeters in twit_scrape_dump.txt with random promo from twit_promos.txt')
    
    # Reddit arguments
    reddit_parser = subparsers.add_parser('reddit', help='Reddit: scrape subreddits, promote to results')
    reddit_parser.add_argument('-s', '--scrape', dest='N', help='scrape subreddits in subreddits.txt for keywords in red_keywords.txt; N = number of posts to scrape')
    categories = reddit_parser.add_mutually_exclusive_group()
    categories.add_argument('-n', '--new', action='store_true', dest='r_new', help='scrape new posts')
    categories.add_argument('-t', '--top', action='store_true', dest='r_top', help='scrape top posts')
    categories.add_argument('-H', '--hot', action='store_true', dest='r_hot', help='scrape hot posts')
    categories.add_argument('-r', '--rising', action='store_true', dest='r_ris', help='scrape rising posts')
    reddit_parser.add_argument('-p', '--promote', action='store_true', dest='r_pro', help='promote to posts in red_scrape_dump.txt not marked with a "-" prefix')

    executed = 0 # catches any command/args that fall through below tree
    args = parser.parse_args()
    
    # twitter handler
    if args.platform == 'twitter':
        # get authentication credentials and api
        authTwitter()

        # update status
        if args.t_upd:
            updateStatus()
            executed = 1

        # scrape twitter for all queries and favorite, follow, and/or promote OPs
        if args.t_scr:
            scrapeTwitter(args.t_con, args.t_eng, args.t_fol, args.t_pro, args.t_dm)
            executed = 1
        else: # otherwise promote to all entries in scrape_dump file
            with open('twit_scrape_dump.txt') as f:
                t_lines = f.readlines()

                reply_count = 0
                
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
                        ret_code = replyToTweet(twt_id, scrn_name)
                        # continue if no error code returned
                        if ret_code is 1:
                            reply_count += ret_code
                        elif ret_code is 2: # automation detected
                            pass #already slept it off, do nothing
                        elif ret_code is 3: # serious error returned, terminate activity
                            log("Prematurely terminating job: replied to {rep} tweets.".format(rep=str(reply_count)))
                            sys.exit(1)
                        
                    if args.t_dm:
                        directMessageTweet(scrn_name)
                
                log("Job done. Replied to {rep} tweets.".format(rep=str(reply_count)))
                
            executed = 1

    # reddit handler
    if args.platform == 'reddit':
        authReddit()

        if args.N:
            scrapeReddit(args.N, args.r_new, args.r_top, args.r_hot, args.r_ris)
            executed = 1

        if args.r_pro:
            replyReddit()
            executed = 1
    
    if not executed:
        log("Unknown Execution Error")
        parser.print_help()
        sys.exit(1)

            
            
# so main() isn't executed if file is imported
if __name__ == "__main__":
    # remove first script name argument
    main(sys.argv[1:])
    
    
    
