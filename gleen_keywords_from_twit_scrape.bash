#!/usr/bin/env bash

# check for null first argument
if [ -z "$1" ]
  then
    	echo "Please specify job directory: e.g. '$(basename "$0") my_job_dir'"
		exit
fi


cat ./$1/twit_scrape_dump.txt | 	# get scrape dump file from command's first argument
sed s/SCRN_NAME/" "/g | 			# seperate meta data from keywords
tr '[:space:]' '[\n*]' | 		# change spaces to newlines
grep -v "^\s*$" | 			# remove blank lines
sort | 					# prepare input to uniq
uniq -dic | 				# eliminate single instance keywords, ignore case
sort -bnr > ./$1/gleened_keywords.txt 	# sort in numeric reverse order, ignore whitespace, output to file 
