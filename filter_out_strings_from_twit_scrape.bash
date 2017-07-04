#!/usr/bin/env bash

# check for null first argument
if [ -z "$1" ]
  then
    	echo "Please specify job directory: e.g. '$(basename "$0") my_job_dir'"
		exit
fi

# TODO read in job's list of strings to filter
#list_to_filter=()
#while IFS='' read -r line || [[ -n "$line" ]]; do
#	list_to_filter+=("$line")
#done < "$1"

cat ./$1/twit_scrape_dump.txt | 	# get scrape dump file from command's first argument
grep -iv chance | 			# remove all these keywords, ignoring case
grep -iv instantwingame | 
grep -iv snrtg |
grep -iv kprs |
grep -iv flockbn |
grep -iv mistylady |
grep -iv points |
grep -iv @SYWSweeps |
grep -iv mature |
grep -iv wonder |
tr -d '\200-\377' > ./$1/twit_scrp_dmp_filtd.txt # remove any non-ascii characters introduced by grep, and print to file
