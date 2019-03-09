import argparse
import getpass
import calendar
import os
import platform
import sys
import urllib.request

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# Global Variables

driver = None

total_scrolls = 20
current_scrolls = 0
scroll_time = 5

old_height = 0


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
            WebDriverWait(driver, scroll_time, 0.05).until(lambda driver: check_height())
            current_scrolls += 1
        except TimeoutException:
            break

    return


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

    return

def extract_and_write_group_posts(filename, elements):
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
                if title.text.find("updated") != -1:
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

    return

def scrape_data(id, scan_list, section, elements_path, file_names):

    page = []
    page.append(id)

    for i in range(len(section)):
        page.append(id + section[i])

    for i in range(len(scan_list)):
        try:
            driver.get(page[i])

            scroll()

            data = driver.find_elements_by_xpath(elements_path[i])

            #extract_and_write_posts(file_names[i], data)
            extract_and_write_group_posts(file_names[i], data)

        except:
            print("Exception (scrape_data)", str(i), "Status =", sys.exc_info()[0])


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


def scrape_profile(ids):

    # execute for all profiles given in input.txt file
    for id in ids:

        driver.get(id)
        url = driver.current_url
        id = create_original_link(url)

        scan_list = [None]
        section = []
        elements_path = ['//div[@class="_5pcb _4b0l _2q8l"]']

        file_names = ["data/posts.txt"]

        scrape_data(id, scan_list, section, elements_path, file_names)
        print("Posts(Statuses) Done")
        print("----------------------------------------")

    return
    
def scrape_groups(groups):

    print("\nScraping groups...")
    for grp in groups:

        
        driver.get(grp)
        url = driver.current_url
        id = create_original_link(url)
        print("Scraping " + id)

        scan_list = [None]
        section = []
        elements_path = ['//div[@class="_5pcb"]']
        file_names = ["data/grp-posts.txt"]

        scrape_data(id, scan_list, section, elements_path, file_names)

        sys.exit()
    return


def login():
    # read in groups to scrape
    f = open("data/credentials.txt")
    creds = f.readlines()
    email = creds[0]
    password = creds[1]
    f.close()
    #email = input('\nEnter facebook email: ')
    #password = getpass.getpass()

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

        driver.find_element_by_name('email').send_keys(email)
        driver.find_element_by_name('pass').send_keys(password)
        driver.find_element_by_id('loginbutton').click()

    except Exception as e:
        print("Error logging in.")
        print(sys.exc_info()[0])
        exit()


def main(argv):

    # read in groups to scrape
    f = open("data/groups.txt")
    groups = f.readlines()
    f.close()
    # read in users to scrape
    #users = ["https://www.facebook.com/" + line.split("/")[-1] for line in open("users.txt", newline='\n')]

    login()

    # scrape groups
    if len(groups) > 0:

        scrape_groups(groups)
        print("Group posts done\n----------------------------------------")
        driver.close()
    else:
        print("Need to populate group.txt with group urls to scrape...")


# so main() isn't executed when script is imported
if __name__ == '__main__':
    main(sys.argv[1:])
