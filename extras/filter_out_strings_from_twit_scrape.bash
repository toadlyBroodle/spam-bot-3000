#!/usr/bin/env bash
cat ../twit_scrape_dump.txt | 	# read from active scrape dump file
grep -iv "wall clock" | 			# remove all these keywords, ignoring case
grep -iv stick |
grep -iv wand |
grep -iv memorial |
tr -d '\200-\377' > twit_scrp_dmp_filtd.txt # remove any non-ascii characters introduced by grep, and print to file
