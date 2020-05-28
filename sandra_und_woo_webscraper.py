# Kevin Mathews 5/27/2020
# Online Web-Scraper to download web-comic images (Configured for the webcomic Sandra und Woo in german)
# Based on exercises from Automate the Boring Stuff with Python by Al Sweigart
# Requires webdrivers are downloaded & configured for selenium

# I AM NOT A BOT. I AM YOUR COLLEAGUE. BEEP BOOP

# Instructions
# Enter ending URL, starting URL, and page # to current_file.txt

# Example End: http://www.sandraandwoo.com/woode/2020/03/30/1165-tiger/
# Example Start: http://www.sandraandwoo.com/woode/2020/05/07/1176-spaeter-besucher/
# Example Page #: 1191

import webbrowser
from selenium import webdriver
import time, sys, os
import random, datetime
from datetime import date, timedelta
import pandas as pd
from bs4 import BeautifulSoup
import requests, re

# input variables
output_folder = os.path.join(os.getcwd(),'image_folder')

# calculate random time to simulate human input
def rand_wait(print_string, lower, upper):
	time.sleep(random.uniform(lower, upper))

def get_image(cur_url, photo_num_str):

	success = 0
	while success == 0:

		try:
			fileName = ''
			time.sleep(random.uniform(1, 3))
			#-----------
			# find image
			#-----------
			
			# body html
			table_element = browser.find_element_by_css_selector('div[id=\"page\"]') # <div id="page-wrap">...</div> == $0
			soup = BeautifulSoup(table_element.get_attribute('outerHTML'), 'html.parser')
			
			#find the comic image
			comicElem = soup.select('#comic img')
			if comicElem == []:
				print('Could not find comic image.')
			else:
				imageUrl = comicElem[0].get('src')

			baseName = cur_url.split('/')[~1] + '.jpg'
			fileName = re.sub('[!@#$/]', '', baseName)
			fileName = photo_num_str.zfill(5) + '_' + fileName
			print(fileName + '...')

			#-------------------
			# modifications (Sandra and Woo)
			#-------------------
			imageUrl = 'http://www.sandraandwoo.com' + imageUrl

			#-------------------
			# download the image
			#-------------------	
			#print('Downloading image %s...' % (imageUrl))
			
			# wait
			browser.get(imageUrl)
			rand_wait(photo_num_str.zfill(5), 2,5)
			res = requests.get(imageUrl)
			res.raise_for_status()
			
			assert fileName != ''
			# download file
			imageFile = open(os.path.join(output_folder, fileName), 'wb')
			for chunk in res.iter_content(100000):
				imageFile.write(chunk)
			imageFile.close()

			browser.get(cur_url)
			
			success = 1
			
		except:
			print('error.')
			browser.get(cur_url) # get webpage
			pass

		return fileName		

current_file = open('current_file.txt','r')
current_list = current_file.readlines()
current_list = [i.replace('\n','') for i in current_list]

current_file.close()

end_url = current_list[0]
cur_url = current_list[1]
photo_num = int(current_list[2])

print('starting...')
browser = webdriver.Chrome() # start web browser

#----------------------
# loop through webpages
#----------------------

browser.get(cur_url) # get webpage

rand_wait(str(photo_num).zfill(5), 5,8) # wait
while cur_url != end_url:

	image_exists = 0
	while image_exists == 0: 
		# download image
		fileName = get_image(cur_url, str(photo_num))
		
		# check if image is in folder
		if os.path.exists(output_folder + '/' + fileName) == True:
			image_exists = 1
		else:
			pass
	
	# increment photo number
	photo_num += 1
	
	# get next link
	nextLink = browser.find_element_by_css_selector('a[rel=\"next\"]')
	
	# set current url
	cur_url = nextLink.get_attribute('href')
	
	# write current url to file
	current_file = open('current_file.txt','w')
	current_file.write(end_url + '\n' + cur_url + '\n' + str(photo_num))
	current_file.close()
	
	# click next button
	nextLink.click()

# get last image
current_file = open('current_file.txt','r')
current_list = current_file.readlines()
current_list = [i.replace('\n','') for i in current_list]
current_file.close()

cur_url = current_list[1]
photo_num = int(current_list[2])

get_image(cur_url, str(photo_num))

# close browser
browser.close()

print('done.')
