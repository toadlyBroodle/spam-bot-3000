#!/usr/bin/env bash

# check for null first argument
if [ -z "$1" ]
  then
    	echo "Please specify job directory: e.g. '$(basename "$0") my_job_dir'"
		exit
fi


cat ./$1/twit_scrape_dump.txt | 	# get scrape dump file from command's first argument
grep -iv "wall clock" | 			# remove all these keywords, ignoring case
grep -iv wand |
grep -iv memorial |
tr -d '\200-\377' > ./$1/twit_scrp_dmp_filtd.txt # remove any non-ascii characters introduced by grep, and print to file
