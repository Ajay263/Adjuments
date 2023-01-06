#Import of Packages
from __future__ import unicode_literals
import youtube_dl
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import pandas as pd
import time


# Function for logging in
def get_driver():
    # set options as you wish
    option = Options()
    option.add_argument("--disable-infobars")
    option.add_argument("start-maximized")
    option.add_argument("--disable-extensions")

    with open('facebook_credentials.txt') as file:  # (a TEXT FILE CONTAINING LOGIN CREDENTIALS)
        EMAIL = file.readline().split('"')[1]
        PASSWORD = file.readline().split('"')[1]

    # Path to webdriver
    driver = webdriver.Chrome(executable_path="./chromedriver", options=option)

    # open the webpage
    driver.get("https://m.facebook.com")
    wait = WebDriverWait(driver, 30)
    email_field = wait.until(EC.visibility_of_element_located((By.NAME, 'email')))
    email_field.send_keys(EMAIL)
    pass_field = wait.until(EC.visibility_of_element_located((By.NAME, 'pass')))
    pass_field.send_keys(PASSWORD)
    pass_field.send_keys(Keys.RETURN)

    time.sleep(5)

    # URL to scrape
    driver.get("https://m.facebook.com/theriverabc")  # once logged in, free to open up any target page

    # Scroll to bottom of the page to trigger JavaScript action
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    WebDriverWait(driver, 30)

    time.sleep(5)
    return driver

if __name__ == "__main__":
  print('Creating driver')
  driver = get_driver()

# Get scroll height
current_scroll_height = driver.execute_script("return document.documentElement.scrollHeight")
print('> Current Scroll Height (before loop):', current_scroll_height)  # starts at 2264

# Locate individual Facebook Video
videos = driver.find_elements(By.XPATH, "//div[@class='story_body_container']")

url_list = []  # Create array forurl list
title_list = []  # Create array for title list
video_list=[]

# Loop: Facebook page load to end of scroll
while True:
    # Scroll to bottom of page
    driver.execute_script("window.scrollTo(0, arguments[0]);", current_scroll_height)
    # Wait to load page
    time.sleep(1)
    print(' - Current Scroll Height (while loop):', current_scroll_height)

    # Extract title, date ,channel & url of  posted videos
    for video in videos:
        title = video.text
        title_list.append(title)
        url_path = video.find_elements(By.XPATH, "//a[@class='_5msj']")
        video_list.append(video)
        for i in url_path:
            url = i.get_attribute('href')
            url_list.append(url)

        # Store individual Facebook video information within dictionary
        vid_item = {
            "title": title_list,
            "url": url_list
        }

    # Use pandas to present main array containing individual videos + number of videos in array
    df = pd.DataFrame.from_dict(vid_item, orient='index')
    df = df.transpose()

    # save to csv
    df.to_csv('Facebook_crawler.csv')

    # Calculate new scroll height and compare with current scroll height
    new_height = driver.execute_script("return document.documentElement.scrollHeight")
    print(' - New Scroll Height (after for loop):', new_height)
    if new_height == current_scroll_height:
        print(df)
        print('\nNumber of Videos (end of for loop):', len(video_list))
        break
    current_scroll_height = new_height
# Quit
# driver.quit()

#Split the values in the title
channel = df['title'].str.split(pat = '\n',n=1 ,expand = True)
Title = df['title'].str.split(pat = '\n',n=2 ,expand = True)
date = channel[1].str.split(pat = ',', expand = True)
#Rearranging the newly added columns from splitting
df.insert(loc =1, column = 'channel', value = channel[0])
df.insert(loc = 2, column = 'Title', value = Title[2])
df.insert(loc = 2, column = 'Date', value = Title[1])
#Drop  thr title column
df.drop('title', axis = 1, inplace = True)

#View your dataframe
df




# using   youtube_dl to download videos using the links in the dataframe


URL=df['url']


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '%(id)s',
    'noplaylist': True,
    'progress_hooks': [my_hook],
    'ignoreerrors': True

}

with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download(URL)








