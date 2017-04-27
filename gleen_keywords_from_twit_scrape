#!/usr/bin/env bash
cat twit_scrape_dump.txt | 	# read from inactive scrape dump file
sed s/TWT_TXT/" "/g | 			# seperate meta data from keywords
tr '[:space:]' '[\n*]' | 		# change spaces to newlines
grep -v "^\s*$" | 			# remove blank lines
grep "#" | 				# filter for hashtags
sort | 					# prepare input to uniq
uniq -dic | 				# eliminate single instance keywords, ignore case, prefix keywords with occurrence counts
sort -bnr > ./extras_inactive/gleened_keywords.txt 	# sort in numeric reverse order, ignore whitespace, output to file 
