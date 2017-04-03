# twatBot
A python command-line bot for automating promotion on social media. Scrape social media with custom queries and promote your product to all relevant results with a single command. <b>Use at your own risk:</b> depending on how specific your custom queries are, your bot could find itself banned from associated social media sites very quickly ;)

## features
- Reddit
	- scrape subreddit(s) for lists of keyword, dump results in local file (red_scrape_dump.txt)
		- seperate keyword lists for AND, OR, NOT search operations (red_subkey_pairs.json)
		- search new, hot, or rising categories
	- reply to posts in red_scrape_dump.txt with random promotion from red_promos.txt
		- ignore posts by marking them in dump file with "-" prefix
	- praw.errors.HTTPException handling
	- write all activity to log (log.txt)
- Twitter
	- update user status
	- scan twitter for list of custom queries, dump results in local file (twit_scrape_dump.txt)
		- scan continuously or in overwatch mode
	- promotion abilities
		- follow original posters
		- favorite relevant tweets
		- reply to relevant tweets with random promotional tweet from file (twit_promos.txt)
		- ignore tweets by marking them in dump file with "-" prefix
	- tweepy exception handling
	- write all activity to log (log.txt)
 
## reddit initial setup
- install <a href="https://github.com/praw-dev/praw">praw</a> python library dependency `pip install praw`
- <a href="https://praw.readthedocs.io/en/v4.0.0/getting_started/configuration/prawini.html">update 'praw.ini'</a> with <a href="https://www.reddit.com/prefs/apps/">your reddit app credentials</a>
	- <a href="http://pythonforengineers.com/build-a-reddit-bot-part-1/">how to register a new reddit app</a>

## reddit usage
```
usage: twatBot.py reddit [-h] [-s N] [-n | -H | -r] [-p]

optional arguments:
  -h,	--help		show this help message and exit
  -s N,	--scrape N	scrape subreddits in subreddits.txt for keywords in red_keywords.txt; N = number of posts to scrape
  -n,	--new		scrape new posts
  -H,	--hot		scrape hot posts
  -r,	--rising	scrape rising posts
  -p,	--promote	promote to posts in red_scrape_dump.txt not marked with a "-" prefix
``` 

## twitter initial setup
- install <a href="https://github.com/tweepy/tweepy">tweepy</a> dependency `pip install tweepy`
- create new 'credentials.py' file in main directory with your twitter credentials
	- <a href="https://www.digitalocean.com/community/tutorials/how-to-create-a-twitterbot-with-python-3-and-the-tweepy-library">a good guide for how to get twitter credentials</a>


```
<credentials.py>
consumer_key = "your_consumer_key"
consumer_secret = "your_consumer_secret"
access_token = "your_access_token"
access_token_secret = "your_access_token_secret"
```

- replace promotional tweets (promoTweets.txt) with your own
	- individual tweets on seperate lines
	- each line must by <= 140 characters long
- replace search queries (queries.txt) with your own
	- individual queries on seperate lines
	- <a href="https://dev.twitter.com/rest/public/search">guide to constructing twitter queries</a>

## twitter usage
```
usage: twatBot.py twitter [-h] [-u] [-s] [-c] [-f] [-p]

optional arguments:
 -h, --help				show this help message and exit
 -u, --update-status	update status with random promo from twit_promos.txt

query:
 -s, --scrape			scrape for tweets matching queries in twit_queries.txt
 -c, --continuous		scape continuously - suppress prompt to continue after 50 results per query

spam:
 -f, --follow			follow original tweeters in twit_scrape_dump.txt
 -p, --promote			favorite tweets and reply to tweeters in twit_scrape_dump.txt with random promo from twit_promos.txt
```

## twitter workflows
    1) continuous mode
		- [-sp] scrape and promote to all tweets matching queries
    2) overwatch mode
		- [-s] scrape first
		- manually edit scrapeDump.txt
			- add '-' to beginning of line to ignore
			- leave line unaltered to promote to
		- [-p] then promote to remaining tweets in scrapeDump.txt

## notes
Future updates will include modules for promoting to facebook, instagram, etc.