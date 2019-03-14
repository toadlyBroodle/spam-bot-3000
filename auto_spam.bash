#!/usr/bin/env bash

# check for missing job argument
if [ -z "$1" ]
  then
    	echo "Please specify job directory: e.g. '$(basename "$0") my_job_dir'"
		exit
fi

#scrape twitter for results
python3 spam-bot-3000.py twitter -scj $1
# remove filtered keywords from scraped TODO handle null filters
bash filter_out_strings_from_twit_scrape.bash $1
# replace job's scraped results with filtered results
mv $1twit_scrape_dump_filtd.txt $1twit_scrape_dump.txt
# spam in browser TODO auto enter login credentials
python3 spam-bot-3000.py twitter -bj $1

echo 'done auto spamming'
