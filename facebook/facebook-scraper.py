import argparse
import getpass
import calendar
import os
import platform
import sys
import urllib.request
import random
import json

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# Global Variables
driver = None
job_dir = ""
total_scrolls = 500
current_scrolls = 0
R = [3, 7] # random scroll time min/max bounds

old_height = 0


def login(login, password):
    global job_dir
    try:
        global driver

        # customize browser behavior
        _browser_profile = webdriver.FirefoxProfile()
        _browser_profile.set_preference("dom.webnotifications.enabled", False)
        #_browser_profile.set_preference("dom.push.enabled", False)

        try:
            driver = webdriver.Firefox(executable_path="../geckodriver", firefox_profile=_browser_profile)
        except:
            print("Need to download latest geckodriver to main directory: https://github.com/mozilla/geckodriver/releases")
            exit()

        driver.get("https://www.facebook.com")
        driver.maximize_window()

        driver.find_element_by_name('email').send_keys(login)
        driver.find_element_by_name('pass').send_keys(password)
        driver.find_element_by_id('loginbutton').click()

    except Exception as e:
        print("Error logging in.")
        print(sys.exc_info()[0])
        exit()


def create_original_link(url):

    if url.find(".php") != -1:
        original_link = "https://www.facebook.com/" + ((url.split("="))[1])

        if original_link.find("&") != -1:
            original_link = original_link.split("&")[0]

    elif url.find("fnr_t") != -1:
        original_link = "https://www.facebook.com/" + ((url.split("/"))[-1].split("?")[0])
    elif url.find("_tab") != -1:
        original_link = "https://www.facebook.com/" + (url.split("?")[0]).split("/")[-1]
    else:
        original_link = url

    #print("original_link= " + original_link)
    return original_link


def check_height():
    new_height = driver.execute_script("return document.body.scrollHeight")
    return new_height != old_height


# scrolls the feed
def scroll():
    global old_height
    current_scrolls = 0

    while (True):
        try:
            if current_scrolls == total_scrolls:
                return

            old_height = driver.execute_script("return document.body.scrollHeight")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            WebDriverWait(driver, random.randint(R[0],R[1]), 0.05).until(lambda driver: check_height())
            current_scrolls += 1
        except TimeoutException:
            break


# Helper Functions for Posts

def get_status(x):
    status = ""
    try:
        status = x.find_element_by_xpath(".//div[@class='_5wj-']").text
    except:
        try:
            status = x.find_element_by_xpath(".//div[@class='userContent']").text
        except:
            pass
    return status


def get_div_links(x, tag):
    try:
        temp = x.find_element_by_xpath(".//div[@class='_3x-2']")
        return temp.find_element_by_tag_name(tag)
    except:
        return ""


def get_title_links(title):
    l = title.find_elements_by_tag_name('a')
    return l[-1].text, l[-1].get_attribute('href')


def get_title(x):
    title = ""
    try:
        title = x.find_element_by_xpath(".//span[@class='fwb fcg']")
    except:
        try:
            title = x.find_element_by_xpath(".//span[@class='fcg']")
        except:
            try:
                title = x.find_element_by_xpath(".//span[@class='fwn fcg']")
            except:
                pass
    finally:
        return title


def get_time(x):
    time = ""
    try:
        time = x.find_element_by_tag_name('abbr').get_attribute('title')
        time = str("%02d" % int(time.split(", ")[1].split()[1]), ) + "-" + str(
            ("%02d" % (int((list(calendar.month_abbr).index(time.split(", ")[1].split()[0][:3]))),))) + "-" + \
               time.split()[3] + " " + str("%02d" % int(time.split()[5].split(":")[0])) + ":" + str(
            time.split()[5].split(":")[1])
    except:
        pass

    finally:
        return time


def extract_and_write_posts(filename, elements):
    try:
        f = open(filename, "w", newline='\r\n')
        f.writelines(' TIME || TYPE  || TITLE || STATUS  ||   LINKS(Shared Posts/Shared Links etc) ' + '\n' + '\n')

        for x in elements:
            try:
                video_link = " "
                title = " "
                status = " "
                link = ""
                img = " "
                time = " "

                # time
                time = get_time(x)

                # title
                title = get_title(x)
                if title.text.find("shared a memory") != -1:
                    x = x.find_element_by_xpath(".//div[@class='_1dwg _1w_m']")
                    title = get_title(x)

                status = get_status(x)
                if title.text == driver.find_element_by_id("fb-timeline-cover-name").text:
                    if status == '':
                        temp = get_div_links(x, "img")
                        if temp == '':  # no image tag which means . it is not a life event
                            link = get_div_links(x, "a").get_attribute('href')
                            type = "status update without text"
                        else:
                            type = 'life event'
                            link = get_div_links(x, "a").get_attribute('href')
                            status = get_div_links(x, "a").text
                    else:
                        type = "status update"
                        if get_div_links(x, "a") != '':
                            link = get_div_links(x, "a").get_attribute('href')

                elif title.text.find(" shared ") != -1:

                    x1, link = get_title_links(title)
                    type = "shared " + x1

                elif title.text.find(" at ") != -1 or title.text.find(" in ") != -1:
                    if title.text.find(" at ") != -1:
                        x1, link = get_title_links(title)
                        type = "check in"
                    elif title.text.find(" in ") != 1:
                        status = get_div_links(x, "a").text

                elif title.text.find(" added ") != -1 and title.text.find("photo") != -1:
                    type = "added photo"
                    link = get_div_links(x, "a").get_attribute('href')

                elif title.text.find(" added ") != -1 and title.text.find("video") != -1:
                    type = "added video"
                    link = get_div_links(x, "a").get_attribute('href')

                else:
                    type = "others"

                if not isinstance(title, str):
                    title = title.text

                status = status.replace("\n", " ")
                title = title.replace("\n", " ")

                line = str(time) + " || " + str(type) + ' || ' + str(title) + ' || ' + str(status) + ' || ' + str(
                    link) + "\n"

                try:
                    f.writelines(line)
                except:
                    print('Posts: Could not map encoded characters')
            except:
                pass
        f.close()
    except:
        print("Exception (extract_and_write_posts)", "Status =", sys.exc_info()[0])


def scrape_profiles(ids):

    for id in ids:

        driver.get(id)
        #url = driver.current_url
        #id = create_original_link(url)

        scroll()

        data = driver.find_elements_by_xpath('//div[@class="_5pcb _4b0l _2q8l"]')
        extract_and_write_posts("data/posts.txt", data)


def buildPostDumpLine(link, time, title, txt, price, location):
    return (time + ' || ' + price + ' || ' + location + '\n' + link + '\n' + title + '\n' + txt.replace("\n", "") + "\n\n")


def keyword_check(title, text, price, location, job):

    # process any submission with title/text fitting and/or/not keywords
    tit_txt = title.lower() + ' ' + text.lower()

    # must not contain any NOT keywords
    for kw in job['keywords_not']:
        if kw in tit_txt:
            return False

    # must contain all AND keywords
    for kw in job['keywords_and']:
        if not kw in tit_txt:
            return False

    # must contain at least one OR keyword
    at_least_one = False
    for kw in job['keywords_or']:
        if kw in tit_txt:
            return True

    return False


def extract_and_write_group_posts(posts, job):
    global job_dir

    with open(job_dir + 'results.txt', 'a') as f:
        for post in posts:
            time = post.find_element_by_tag_name('abbr').get_attribute('title')
            link = post.find_element_by_xpath(".//span[@class='fsm fwn fcg']/a").get_attribute('href')

            try:
                title = post.find_element_by_xpath(".//div[@class='_l53']/span[2]").text
            except NoSuchElementException as e:
                title = ''
            try:
                text = post.find_element_by_xpath('.//div[@class="_l52"]/div[2]/p').text
            except NoSuchElementException as e:
                text = ''
            try:
                price = post.find_element_by_xpath('.//div[@class="_l57"]').text
            except NoSuchElementException as e:
                price = ''
            try:
                location = post.find_element_by_xpath('.//div[@class="_l58"]').text.replace('::before','')
            except NoSuchElementException as e:
                location = ''

            if keyword_check(title, text, price, location, job):
                f.write(buildPostDumpLine(link,time,title,text,price,location))


def scrape_groups(job):

    print("\nScraping groups...")
    for grp in job['urls']:

        driver.get(grp)
        url = driver.current_url
        id = create_original_link(url)

        print("Scraping " + id)
        scroll()
        elements_path = []
        posts = driver.find_elements_by_xpath('//div[@class="_1dwg _1w_m _q7o"]')
        extract_and_write_group_posts(posts, job)


def main(argv):
    global job_dir
    client_data = []

    # check for input arguments
    if not argv:
        print("Must specify input arguments, e.g. 'python3 facebook-scraper.py JOB_DIR/'")
        sys.exit()

    # read in client data
    job_dir = argv[0]
    with open(job_dir + 'client_data.json') as json_data:
        parsed = json.load(json_data)
        client_data = parsed['client_data']

    login(client_data['fb_login'], client_data['fb_password'])

    # scrape jobs
    for job in client_data['jobs']:
        #if job['type'] == 'users':
        #    scrape_profiles(job)
        if job['type'] == 'groups':
            scrape_groups(job)

    driver.close()

# so main() isn't executed when script is imported
if __name__ == '__main__':
    main(sys.argv[1:])
