# twatBot
A python command-line bot for automating promotion on social media. Scrape social media with custom queries and promote your product to all relevant results with a single command. <b>Use at your own risk:</b> depending on how specific your custom queries are, your bot could find itself banned from associated social media sites very quickly ;)

## features
- Twitter
	- update user status
	- scan twitter for list of custom queries, dump results in local file (scrapeDump.txt)
		- follow original posters
		- favorite relevant tweets
		- reply to relevant tweets with random promotional tweet from file (promoTweets.txt)
		- write all activity to log (log.txt)

## reddit initial setup
- install praw python library dependency `pip install praw`
- <a href="https://praw.readthedocs.io/en/v4.0.0/getting_started/configuration/prawini.html">update praw.ini</a> with <a href="http://pythonforengineers.com/build-a-reddit-bot-part-1/">your reddit app credentials</a>
 
 
## twitter initial setup
- install tweepy dependency `pip install tweepy`
- create new 'credentials.py' file in main directory with your twitter credentials
	- <a href="https://www.digitalocean.com/community/tutorials/how-to-create-a-twitterbot-with-python-3-and-the-tweepy-library">a good guide for how to get twitter credentials</a>

<credentials.py>
```
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

## usage
usage: twatBot.py twitter [-h] [-s] [-f] [-p] [-u]

optional arguments:
- -h, --help           		show this help message and exit
- -u, --update-status update status with random promo from promoTweets.txt

promotion:
- -s, --scrape       		scrape for tweets matching query
- -f, --follow         		follow original tweeters in scrapeDump.txt
- -p, --promote        	favorite tweets and reply to tweeters in scrapeDump.txt with random promo from promoTweets.txt

## notes
Future updates will include modules for promoting to reddit, facebook, instagram, etc.