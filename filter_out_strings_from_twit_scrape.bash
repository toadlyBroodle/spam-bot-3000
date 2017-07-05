#!/usr/bin/env bash

# check for null first argument
if [ -z "$1" ]
  then
    	echo "Please specify job directory: e.g. '$(basename "$0") my_job_dir'"
		exit
fi

# get | delimeted string of edited keywords to filter out
delimStr=$(cat ./$1gleened_keywords.txt | tr "\n" "|")
# remove lines containing strings to filter out
grep -vE "($delimStr)" ./$1twit_scrape_dump.txt |
# remove any non ascii characters from dump file
tr -d '\200-\377' > ./$1twit_scrape_dump_filtd.txt

echo 'done'