# spam-bot-3000
A python command-line (CLI) bot for automating research and promotion on popular social media platforms (reddit, twitter, facebook, [TODO: instagram]). With a single command, scrape social media sites using custom queries and/or promote to all relevant results.

<b>Please use with discretion:</b> i.e. choose your input arguments wisely, otherwise your bot could find itself, along with any associated accounts, banned from platforms very quickly. The bot has some built in anti-spam filter avoidance features to help you remain undetected; however, no amount of avoidance can hide blatantly abusive use of this tool.

## features
- reddit
	- scrape subreddit(s) for lists of keyword, dump results in local file (red_scrape_dump.txt)
		- separate keyword lists for AND, OR, NOT search operations (red_subkey_pairs.json)
		- search new, hot, or rising categories
	- reply to posts in red_scrape_dump.txt with random promotion from red_promos.txt
		- ignore posts by marking them in dump file with "-" prefix
	- praw.errors.HTTPException handling
	- write all activity to log (log.txt)
- twitter
	- maintain separate jobs for different promotion projects
	- update user status
	- unfollow users who don't reciprocate your follow
	- scan twitter for list of custom queries, dump results in local file (twit_scrape_dump.txt)
		- scan continuously or in overwatch mode
	- optional bypassing of proprietary twitter APIs and their inherent limitations
	- promotion abilities
        - tweepy api
		    - follow original posters
		    - favorite relevant tweets
		    - direct message relevant tweets
		    - reply to relevant tweets with random promotional tweet from file (twit_promos.txt)
        - Selenium GUI browser
            - favorite, follow, reply to scraped results while bypassing API limits	    
        - ignore tweets by marking them in dump file with "-" prefix
	- script for new keyword, hashtag research by gleening scraped results
	- script for filtering out irrelevant keywords, hashtags, screen names
	- script for automating scraping, filtering, and spamming only most relevant results
	- relatively graceful exception handling
	- write all activity to log (log.txt)
- facebook
	- zero reliance on proprietary facebook APIs and their inherent limitations
	- Selenium GUI browser agent
	- scrape public and private user profiles for keywords using AND, OR, NOT operators
		- note: access to private data requires login to authorized account with associated access
	- scrape public and private group feeds for keywords using AND, OR, NOT operators

## dependencies
- install dependencies you probably don't have already, errors will show up if you're missing any others
	- install pip3 `sudo apt install python3-pip`
	- install dependencies `pip3 install --user tweepy bs4 praw selenium`

## reddit initial setup
- <a href="https://praw.readthedocs.io/en/v4.0.0/getting_started/configuration/prawini.html">update 'praw.ini'</a> with <a href="https://www.reddit.com/prefs/apps/">your reddit app credentials</a>
	- <a href="http://pythonforengineers.com/build-a-reddit-bot-part-1/">how to register a new reddit app</a>
- replace example promotions (red_promos.txt) with your own
- replace example subreddits and keywords (red_subkey_pairs.json) with your own
	- you'll have to follow the existing json format
	- `keywords_and`: all keywords in this list must be present for positive matching result
	- `keywords_or`: at least one keyword in this list must be present for positive match
	- `keywords_not`: none of these keywords can be present in a positive match
	- any of the three lists may be omitted by leaving it empty - e.g. `"keywords_not": []`

<praw.ini>
```
...

[bot1]
client_id=Y4PJOclpDQy3xZ
client_secret=UkGLTe6oqsMk5nHCJTHLrwgvHpr
password=pni9ubeht4wd50gk
username=fakebot1
user_agent=fakebot 0.1
```

<red_subkey_pairs.json>
```
{"sub_key_pairs": [
{
  "subreddits": "androidapps",
  "keywords_and": ["list", "?"],
  "keywords_or": ["todo", "app", "android"],
  "keywords_not": ["playlist", "listen"]
}
]}
```

## reddit usage
```
usage: spam-bot-3000.py reddit [-h] [-s N] [-n | -H | -r] [-p]

optional arguments:
  -h,	--help		show this help message and exit
  -s N,	--scrape N	scrape subreddits in subreddits.txt for keywords in red_keywords.txt; N = number of posts to scrape
  -n,	--new		scrape new posts
  -H,	--hot		scrape hot posts
  -r,	--rising	scrape rising posts
  -p,	--promote	promote to posts in red_scrape_dump.txt not marked with a "-" prefix
```

## twitter initial setup
- create new directory to store new job data in (e.g. studfinder_example/)
- create new 'credentials.txt' file in job directory to store your twitter app's credentials
	- <a href="https://www.digitalocean.com/community/tutorials/how-to-create-a-twitterbot-with-python-3-and-the-tweepy-library">a good guide for how to get twitter credentials</a>

<credentials.txt>
```
your_consumer_key
your_consumer_secret
your_access_token
your_access_token_secret
your_twitter_username
your_twitter_password
```

- create new 'twit_promos.txt' in job directory to store your job's promotions to spam
	- individual tweets on seperate lines
	- each line must by <= 140 characters long
- create new 'twit_queries.txt' in job directory to store your job's queries to scrape twitter for
	- individual queries on seperate lines
	- <a href="https://dev.twitter.com/rest/public/search">guide to constructing twitter queries</a>
- create new 'twit_scrape_dump.txt' file to store your job's returned scrape results

## twitter usage
```
usage: spam-bot-3000.py twitter [-h] [-j JOB_DIR] [-t] [-u UNF] [-s] [-c] [-e] [-b]
                          [-f] [-p] [-d]
spam-bot-3000
optional arguments:
 -h, --help		show this help message and exit
 -j JOB_DIR, --job JOB_DIR
	                choose job to run by specifying job's relative directory
 -t, --tweet-status 	update status with random promo from twit_promos.txt
 -u UNF, --unfollow UNF
                        unfollow users who aren't following you back, UNF=number to unfollow

 query:
 -s, --scrape		scrape for tweets matching queries in twit_queries.txt
 -c, --continuous	scape continuously - suppress prompt to continue after 50 results per query
 -e, --english         	return only tweets written in English

spam -> browser:
 -b, --browser          favorite, follow, reply to all scraped results and
                        thwart api limits by mimicking human in browser!

spam -> tweepy api:
 -f, --follow		follow original tweeters in twit_scrape_dump.txt
 -p, --promote		favorite tweets and reply to tweeters in twit_scrape_dump.txt with random promo from twit_promos.txt
 -d, --direct-message	direct message tweeters in twit_scrape_dump.txt with random promo from twit_promos.txt
```

## twitter example workflows
1) continuous mode
	- `-cspf` scrape and promote to all tweets matching queries
2) overwatch mode
	- `-s` scrape first
	- manually edit twit_scrape_dump.txt
		- add '-' to beginning of line to ignore
		- leave line unaltered to promote to
	- `-pf` then promote to remaining tweets in twit_scrape_dump.txt
3) gleen common keywords, hashtags, screen names from scrape dumps
	- `bash gleen_keywords_from_twit_scrape.bash`
		- input file: twit_scrape_dump.txt
		- output file: gleened_keywords.txt
            - results ordered by most occurrences first
4) filter out keywords/hashtags from scrape dump
    - manually edit gleened_keywords.txt by removing all relevent results
    - `filter_out_strings_from_twit_scrape.bash`
        - keywords input file: gleened_keywords.txt		
        - input file: twit_scrape_dump.txt
		- output file: twit_scrp_dmp_filtd.txt
5) browser mode
    - `-b` thwart api limits by promoting to scraped results directly in firefox browser
		- add username and password to lines 5 and 6 of credentials.txt respectively
6) automatic scrape, filter, spam
	- `auto_spam.bash`
		- automatically scrape twitter for queries, filter out results to ignore, and spam remaining results
7) specify job
    - `-j studfinder_example/` specify which job directory to execute

Note: if you don't want to maintain individual jobs in separate directories, you may create single credentials, queries, promos, and scrape dump files in main working directory.

## facebook initial setup
- create new client folder in 'facebook/clients/YOUR_CLIENT'
- create new 'jobs.json' file to store your client's job information in the following format:

<jobs.json>
```
{"client_data":
	{"name": "",
	"email": "",
	"fb_login": "",
	"fb_password": "",
	"jobs": [
		{"type": "groups",
			"urls": ["",""],
			"keywords_and": ["",""],
			"keywords_or": ["",""],
			"keywords_not": ["",""] },
		{"type": "users",
			"urls": [],
			"keywords_and": [],
			"keywords_or": [],
			"keywords_not": [] }
	]}
}
```

## facebook usage
- scrape user and group feed urls for keywords
	- `facebook-scraper.py clients/YOUR_CLIENT/`
		- results output to 'clients/YOUR_CLIENT/results.txt'

## TODO
- Flesh out additional suite of promotion and interaction tool for facebook platform
- Organize platforms and their associated data and tools into their own folders and python scripts
- Future updates will include modules for scraping and promoting to Instagram.
