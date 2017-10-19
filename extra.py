#############################################################
# The model that accesses the data from the Heroku Database
# The data here is either sorted into a category or filtered 
# by specific component and sent back to be displayed by the 
# crud.py
# 
# Edited: Logan
# Edited: Grant
##############################################################

from __future__ import print_function
from apiclient import discovery
from oauth2client import client
#from oayth2client.client import SignedJwtAssertionCredentials
from oauth2client import tools
from oauth2client.file import Storage
#from bookshelf import oauth2
from flask import Blueprint, current_app, redirect, render_template, request, \
	session, url_for
import httplib2
import os
import gspread
from xlrd import open_workbook
import os
import psycopg2
import urlparse
import sys
import csv

try:
	import argparse
	flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
	flags = None

#count of solvers
count = 0
#count of contributors
count2 = 0

final=[]
##############################################################
# Pulls all of the values that are being used for the current
# non-sorted table
#
# limit: amount of records shown on one page
# page_token: current page number
##############################################################
def get_values(limit, page_token, current):
	cur = current
	list = []
	list2 = cur.fetchall()
	for i in list2:
		values = []
		for a in i:
			if(a is None):
             			values.append('')
          		else:
             			values.append(a)
       		list.append(values) 
	count_contributors(list)
	list = sorted(list, key=lambda x: x[0])

	cursor = page_token if page_token else 0
	values = list[cursor * 50 : cursor * 50 + 50]
	return values
	
##############################################################
# Pulls all of the values that are being used for the current
# non-sorted table
#
# limit: amount of records shown on one page
# page_token: current page number
##############################################################
def get_values_adv(limit, page_token, current, mqvol, mqvol2, etvol, etvol2, etdate, etdate2, mqdate, mqdate2):
    	cur = current
    	list = []
    	list2 = cur.fetchall()
    	for i in list2:
       		values = []
       		for a in i:
          		if(a is None):
             			values.append('')
          		else:
             			values.append(a)
       		list.append(values)
 	list = sorted(list, key=lambda x: x[3])
    	if mqvol != 'zyx' and mqvol2 != 'zyx':
        	list = compVol(list, mqvol, mqvol2, 7)
    	if etvol != 'zyx' and etvol2 != 'zyx':
        	list = compVol(list, etvol, etvol2, 5)
    	if etdate != 'zyx' and etdate2 != 'zyx':
        	list = compDate(list, etdate, etdate2, 2)
    	if mqdate != 'zyx' and mqdate2 != 'zyx':
        	list = compDate(list, mqdate, mqdate2, 6)   
	count_contributors(list)
    	list = sorted(list, key=lambda x: x[0])

    	cursor = page_token if page_token else 0
    	values = list[cursor * 50 : cursor * 50 + 50]
    	return values

##############################################################
# Pulls the data from Heroku Database
# Searches the data pulled and finds direct matches for 
# simple proposer search
#
# limit: amount of records shown on one page
# page_token: current page number
# search: the value being searched
##############################################################
def get_valuesx(limit, page_token, search):
    	cur = psql() 
    	list = []
    	list2 = cur.fetchall()
    	for i in list2:
       		values = []
       		for a in i:
          		if(a is None):
             			values.append('')
          		else:
             			values.append(a)
       		list.append(values)
    	page_token = page_token if page_token else 0
    	values = list
    	values = sorted(values, key=lambda x: x[0])


    	temp2 = []
    	y=0
    	temp3 = []
    	for row in values:
       		if(search.lower() in row[3].lower()):
           		temp3.append(row)
    	count_contributors(temp3)
    	for row in values:
       		if(search.lower() in row[3].lower() and limit * page_token <= y and limit + limit * page_token > y):
           		temp2.append(row)
           		y = y + 1;
       		elif(search.lower() in row[3].lower()):
           		y = y + 1
    	return temp2;

##############################################################
# Pulls the data from Heroku Database
# Searches the data pulled and finds direct matches to the 
# last name of proposer
# Also sorts them alphabetically
#
# limit: amount of records shown on one page
# page_token: current page number
# search: the value being searched
##############################################################
def get_valuesy(limit, page_token, search):
    	cur = psql()
    	list = []
    	list2 = cur.fetchall()
    	for i in list2:
       		values = []
       		for a in i:
          		if(a is None):
             			values.append('')
          		else:
             			values.append(a)
       		list.append(values)
    	values = list
    	values = sorted(values, key=lambda x: x[3])
    	values.reverse()
    	values = sorted(values, key=lambda x: (x[3].split(' '))[len(x[3].split(' ')) - 1])
    	values.reverse()
    	values = sorted(values, key=lambda x: len(x[3].split(' ')))
 
    	page_token = page_token if page_token else 0
    	temp2 = []
    	y = 0
    	temp3 = []
    	for row in values:
       		if(search in row[3] and limit * page_token <= y and limit + limit * page_token > y and " " not in row[3] and search == row[3][0]):
           		temp2.append(row)
           		y = y + 1
       		elif((" " + search) in row[3] and limit * page_token <= y and limit + limit * page_token > y):
           		temp2.append(row)
           		y = y + 1
       		elif(search in row[3] and " " not in row[3] and search ==row[3][0]):
           		y = y + 1
       		elif((" " + search) in row[3]):
           		y = y + 1 
    	for row in values:
       		if(search in row[3] and " " not in row[3] and search == row[3][0]):
           		temp3.append(row)
       		elif((" " + search) in row[3]):
           		temp3.append(row)
    	count_contributors(temp3)
    	return temp2;

##############################################################
# Searches the list for values of volume that are between them
# and returns the new list
##############################################################
def compVol(list, mqvol, mqvol2, bit):
    	list2 = []
    	for row in list:
        	for vol in row[bit].split('\n'):
            		print(vol)
            		try:
                 		if vol != None and vol.strip() != "" and vol.strip() != " " and float(vol.strip()) >= float(mqvol) and float(vol.strip()) <= float(mqvol2):
                     			if row not in list2:
                        			list2.append(row)
            		except ValueError:
                 		pass
    	return list2

##############################################################
# Searches the list for values of dates that are between them
# and returns the new list
##############################################################
def compDate(list, date, date2, bit):
    	date = date.split('\n')
    	year = date[0][2:]
    	year = year[:-6]
    	month2 = date[0][5:-3] 
    	date2 = date2.split('\n')
    	year2 = date2[0][2:]
    	year2 = year2[:-6]
    	month3 = date2[0][5:-3]
    	list2=[]
    	for row in list:
        	for date3 in row[bit].replace("-", " ").split('\n'):
            		try:
                 		month = date3[0] +date3[1]+date3[2]
                 		year3 = date3[4:]
                 		if month == 'Jan':
                     			month = 1
                 		elif month == 'Feb':
                     			month = 2
                 		elif month == 'Mar':
                     			month = 3
                 		elif month == 'Apr':
                     			month = 4
                 		elif month == 'May':
                     			month = 5
                 		elif month == 'Jun':
                     			month = 6
                 		elif month == 'Jul':
                     			month = 7
                 		elif month == 'Aug':
                     			month = 8
                 		elif month == 'Sep':
                     			month = 9
                 		elif month == 'Oct':
                     			month = 10
                 		elif month == 'Nov':
                     			month = 11
                 		elif month == 'Dec':
                     			month = 12
                 		else:
                     			month = 0
                 		if float(year3) > float(year) and float(year3) < float(year2) and row not in list2:
                     			list2.append(row)
                 		elif float(year3) == float(year) and float(year3) == float(year2):
                     			if month >= float(month2) and month <= float(month3) and row not in list2:
                         			list2.append(row)
                 		elif float(year3) == float(year) and float(year3) < float(year2):
                     			if month >= float(month2) and row not in list2:
                         			list2.append(row)
                 		elif float(year3) > float(year) and float(year3) == float(year2):
                     			if month <= float(month3) and row not in list2:
                         			list2.append(row)
            		except ValueError:
	         		pass
            		except IndexError:
                 		pass
                 
    	return list2

##############################################################
# Counts the amount of total solvers in all of Educational 
# Times
##############################################################
def count_authors(list):
    	global count
	global final
	list = sorted(list, key=lambda x: x[0])
	try:
		os.remove("expa.csv")
	except Exception:
		pass
    	with open('expa.csv','w') as myfile:
        	wr = csv.writer(myfile)
        	wr.writerow(['NUM','ET VOL','DATE','PROPOSER','SOLVERS','ET VOL','DATE','MQ VOL','TYPE'])
        	for item in list:
            		wr.writerow([item[0],item[1],item[2],item[3],item[4],item[5],item[6],item[7],item[8]])
			print(item[0])
		myfile.close()
	with open('expa.csv','r') as myfile:
		reader = csv.reader(myfile, delimiter=' ',quotechar='|')
		for row in reader:
			print(' '.join(row))
    	count = 0
    	temp = []
    
    	for row in list:
        	for name in row[3].split('\n'):
            		if name not in temp:
                		count = count + 1
                		temp.append(name)
	final = list

def get_final():
	return final
	
##############################################################
# Counts the amount of total proposers in all of Educational
# Times
##############################################################
def count_contributors(list):
    	global count2
    	#list = get_values(0,'')
    	count2 = len(list)
    	count_authors(list)

##############################################################
# Returnns the totla amount of authors
##############################################################
def gcount_authors():
    	return count

##############################################################
# Returns the total amount of contributors
##############################################################
def gcount_contributors():
    	return count2

##############################################################
# Returns the whole searched list without limiting them
##############################################################
def gwhole_list():
    	return wholeList

##############################################################
# Returns the current connection to the database
##############################################################
def psql():
    	urlparse.uses_netloc.append("postgres")
    	url = urlparse.urlparse(os.environ["DATABASE_URL"])

    	conn = psycopg2.connect(
       		database=url.path[1:],
       		user=url.username,
       		password=url.password,
       		host=url.hostname,
       		port=url.port
    	)
    	cur = conn.cursor()
    	reload(sys)
    	sys.setdefaultencoding('utf-8')
    	cur.execute("select * from educational")
    	return cur
	
##############################################################
# Returns the current connection to the database
##############################################################
def psql2(number, etvol, etvol2, proposer, solver, qtype):
    	urlparse.uses_netloc.append("postgres")
    	url = urlparse.urlparse(os.environ["DATABASE_URL"])

    	conn = psycopg2.connect(
       		database=url.path[1:],
       		user=url.username,
       		password=url.password,
       		host=url.hostname,
      	 	port=url.port
    	)
    	query="select * from educational where "
    	if number != "zyx":
       		query += "number = '{0}' and ".format(number)
    	if etvol != "zyx" and etvol2 != "":
       		query += "etvol >= '{0}' and etvol <= '{1}' and ".format(etvol, etvol2)
    	if proposer != "zyx":
       		query += "UPPER(proposer) like UPPER('%{0}%') and ".format(proposer)
    	if solver != "zyx":
       		query += "UPPER(solver) like UPPER('%{0}%') and ".format(solver)
    	if qtype != "zyx":
       		query += "qtype like '%{0}%' and ".format(qtype)
    	query += "true"
    	cur = conn.cursor()
    	reload(sys)
    	sys.setdefaultencoding('utf-8')
    	cur.execute(query)
    	return cur
