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
grep -iv RT | 			# remove all these keywords, ignoring case
grep -iv Via | 
grep -iv spectacular |
grep -iv points |
grep -iv "50" |
grep -iv Enter |
grep -iv wonder |
grep -iv mature |
grep -iv @SYWSweeps |
grep -iv PORTER-CABLE |
grep -iv @Tool_Time_UK: |
grep -iv https://t.co/hyMxryNTq2 |
grep -iv https://t.co/rXwvhYF1j7 |
grep -iv https://t.co/KWsYxZEnJm |
grep -iv https://t.co/N8guIiTgLA |
tr -d '\200-\377' > ./$1/twit_scrp_dmp_filtd.txt # remove any non-ascii characters introduced by grep, and print to file
