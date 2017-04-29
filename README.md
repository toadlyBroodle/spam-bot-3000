# twatBot
A python command-line (CLI) bot for automating promotion on popular social media sites (reddit, twitter; in progress: instagram, facebook). Scrape social media with custom queries and promote your product to all relevant results with a single command. 
<b>Use at your own risk:</b> depending on how specific your custom queries are, your bot could find itself (and likely it's associated accounts) banned from social media sites very quickly ;)

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
	- maintain seperate jobs for different promotion projects
	- update user status
	- unfollow users who don't reciprocate your follow
	- scan twitter for list of custom queries, dump results in local file (twit_scrape_dump.txt)
		- scan continuously or in overwatch mode
	- promotion abilities
		- follow original posters
		- favorite relevant tweets
		- direct message relevant tweets
		- reply to relevant tweets with random promotional tweet from file (twit_promos.txt)
		- ignore tweets by marking them in dump file with "-" prefix
	- script for new keyword and hashtag research and gleening from scraped results
	- script for filtering out of irrelevant keywords/hashtags
	- tweepy exception handling
	- write all activity to log (log.txt)
 
## reddit initial setup
- install pip3 `sudo apt install python3-pip`
- install <a href="https://github.com/praw-dev/praw">praw</a> python library dependency `pip3 install praw`
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
- install <a href="https://github.com/tweepy/tweepy">tweepy</a> dependency `pip3 install tweepy`
- create new directory to store new job data in (i.e. twit_studfinder_example/)
- create new 'credentials.txt' file in job directory to store your twitter app's credentials
	- <a href="https://www.digitalocean.com/community/tutorials/how-to-create-a-twitterbot-with-python-3-and-the-tweepy-library">a good guide for how to get twitter credentials</a>

<credentials.txt>
```
your_consumer_key
your_consumer_secret
your_access_token
your_access_token_secret
```

- create new 'twit_promos.txt' in job directory to store your job's promotions to spam 
	- individual tweets on seperate lines
	- each line must by <= 140 characters long
- create new 'twit_queries.txt' in job directory to store your job's queries to scrape twitter for
	- individual queries on seperate lines
	- <a href="https://dev.twitter.com/rest/public/search">guide to constructing twitter queries</a>

## twitter usage
```
usage: twatBot.py twitter [-h] [-j JOB_DIR] [-u UNF] [-t] [-s] [-c] [-f] [-p]

optional arguments:
 -h, --help				show this help message and exit
 -j JOB_DIR, --job JOB_DIR
						choose job to run by specifying job's relative directory
 -u UNF, --unfollow UNF
                        unfollow users who aren't following you back, UNF=number to unfollow
 -t, --tweet-status 	update status with random promo from twit_promos.txt

 query:
 -s, --scrape			scrape for tweets matching queries in twit_queries.txt
 -c, --continuous		scape continuously - suppress prompt to continue after 50 results per query
 -e, --english         	return only tweets written in English

spam:
 -f, --follow			follow original tweeters in twit_scrape_dump.txt
 -p, --promote			favorite tweets and reply to tweeters in twit_scrape_dump.txt with random promo from twit_promos.txt
 -d, --direct-message	direct message tweeters in twit_scrape_dump.txt with random promo from twit_promos.txt
```

## twitter workflows
1) continuous mode
	- `-csp` scrape and promote to all tweets matching queries
2) overwatch mode
	- `-s` scrape first
	- manually edit twit_scrape_dump.txt
		- add '-' to beginning of line to ignore
		- leave line unaltered to promote to
	- `-p` then promote to remaining tweets in twit_scrape_dump.txt
3) gleen new keywords and hashtags from scrape dumps
	- `bash gleen_keywords_from_twit_scrape.bash`
		- input file: twit_scrape_dump.txt
		- output file: extras/gleened_keywords.txt
	- `bash gleen_hashtags_from_twit_scrape.bash`
		- input file: twit_scrape_dump.txt
		- output file: extras/gleened_hashtags.txt
4) filter out keywords/hashtags from scrape dump
	- 'filter_out_strings_from_twit_scrape.bash'
		- input file: twit_scrape_dump.txt
		- output file: extras/twit_scrp_dmp_filtd.txt

## notes
If you don't want to maintain individual jobs in separate directories, you may create single credentials, queries, promos, and scrape dump files in main working directory.

Future updates will include modules for promoting to instagram, facebook, etc.
