#V14
from bs4 import BeautifulSoup
import requests
import textwrap
import pandas
import datetime
import urllib.request
import re
import sys
from datetime import date
from datetime import time
from urllib.request import urlopen
import os.path
from os import path
import os
import glob,os
import math
import smtplib 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path


n = len(sys.argv)

if(n!=2 | n!=7):
    print('Usage: yachrworld.py searchparamsfile [SMPT server \'from email\' \'to email\' \'userid\' \'password\']')
    print('Where:')
    print('%searchparamsfile% is file with search parameters.')
    print('If you ')
    exit()


# Arguments passed
#print("\nName of Python script:", sys.argv[0])
 
#print("\nArguments passed:", end = " ")
#for i in range(1, n):
#   print(sys.argv[i], end = " ")


# print(sys.argv[1])
configfile=(sys.argv[1])

if n==2:    
    configfile=(sys.argv[1])
else:
    smtpserver=(sys.argv[2])
    fromemail=(sys.argv[3])
    toemail=(sys.argv[4])
    emailuser=(sys.argv[5])
    emailpassword=(sys.argv[6])


#os.chdir("./boats")
#numberofboatsstored = 0
#numberofboatstoredarray=[]
#for file in glob.glob("./boats/*.*"):
#    numberofboatstoredarray.append(file)
#    print(numberofboatstoredarray[numberofboatsstored])
#    numberofboatsstored=numberofboatsstored+1


if os.path.isfile('./'+configfile):
    data = pandas.read_csv ('./'+configfile)
    config = pandas.DataFrame(data)
    configs = config.loc[0]
    boatbrand=str(configs["Boat Brand"])
    fromyear=str(configs["From Year"])
    toyear=str(configs["To Year"])
    fromlength=str(configs["From Length"])
    tolength=str(configs["To Length"])
    boattype=str(configs["Boat Type"])
else:
    print("Missing config file")
    print("Please create a comma delimited file with first line as follows: ")
    print("Boat Brand,From Year,To Year,From Length,To Length,Boat Type")
    print("And second line comma delimited seach values with the same sequence as the anove headings.")
    exit()

email = smtplib.SMTP('smtp.gmail.com', 587) 
email.starttls() 
email.login("garbage@pio.ca", "Aa4319610773") 


base_url="https://au.yachtworld.com/core/listing/cache/searchResults.jsp?slim=quick&sm=3&currencyid=100&searchtype=homepage&Ntk=boatsUK&luom=126&toLength="+tolength+"&N=1783&cit=true&fromLength="+fromlength+"&toYear="+toyear+"&type=%28Power%29&fromYear="+fromyear+"&man="+boatbrand+"&ps=10"
print(base_url)
#base_url="https://www.yachtworld.com/boats-for-sale/condition-used/type-"+boattype+"/region-northamerica/country-united-states/sort-length:asc/?year="+fromyear+"-"+toyear+"&length="+fromlength+"-"+tolength+"&makeModel="+boatbrand
#base_url="https://www.yachtworld.com/boats-for-sale/condition-used/?makeModel=meridian"
#print(base_url)
now = datetime.datetime.now()

html_page = urllib.request.urlopen(base_url)
soup=BeautifulSoup((html_page.read()),"html.parser")

numboats=soup.find("div", {'class':'searchResultsCount--mobile-container__searchResultsCount'})
if numboats:
    numberofboats = str(soup.find("div", {'class':'searchResultsCount--mobile-container__searchResultsCount'}).text.replace("\n","").replace("*","").replace(" ","").replace("Items",""))
else:    
    print('No Boats found in search')
    exit()

filename=boatbrand+"_"+fromyear+"-"+toyear+"_"+fromlength+"-"+tolength
boatdirectory=filename
Path("./"+boatdirectory).mkdir(parents=True, exist_ok=True)


#numofpriorlisting is the number of listings we have in our saved summary file
priorlistings=pandas.DataFrame()
copyofpriorlistings=pandas.DataFrame()

if os.path.isfile('./'+boatdirectory+'/'+filename+'summary.csv'):
    data = pandas.read_csv ('./'+boatdirectory+'/'+filename+'summary.csv',sep="|")
    priorlistings = pandas.DataFrame(data)
    copyofpriorlistings = pandas.DataFrame(data)
    numofpriorlistings = priorlistings.shape[0]
else:
    numofpriorlistings=0

#print(numberofboats)
numberofchangedprices=0
numofnewlistings=0
numofactivelistings=0
productidall=[]

for page in range(0,int(numberofboats),10):
    html_page = urllib.request.urlopen(base_url+"&No="+str(page))
#    print(base_url+"&No="+str(page))
    soup=BeautifulSoup((html_page.read()),"html.parser")
#    numofactivelistings=0
    productid=[]
    producturl=[]
## this loops to get product number
    for link in soup.findAll('a', attrs={'href': re.compile("^https://au.yachtworld")}):
            result=link.get('data-reporting-click-product-id')
            href=link.get('href')
            if result:
                if result in productid:
                    dummy=0
                else:
                    productid.append(link.get('data-reporting-click-product-id'))
                    productidall.append(link.get('data-reporting-click-product-id'))
                    producturl.append(link.get('href'))
                    numofactivelistings=numofactivelistings+1
    all1=soup.find_all("div",{"class":"listing row"})
    all2=soup.find_all("div",{"class":"listing premier row"})
    all=all1+all2
    counter=0
    for item in all:
        d={}
        #listingnum is the number of the listing for the boat from the search results
        #productid is the array that has all prodcut ids from the search results
        listingmum = (productid[counter])
        price=item.find("div",{"class":"price"})
        if price:
            if item.find("div",{"class":"price"}).text.replace("\n","").replace("*","").replace(" ","") == 'Call$(".currNote").hide()':
                listingprice=("Call for current price")
            else:
                listingprice=(item.find("div",{"class":"price"}).text.replace("\n","").replace("*","").replace(" ","").replace("Can$","").replace(u"\xa0","").replace(",",""))
        #Loop to see if listing number is in prior listings
        boatfound=0
        if numofpriorlistings != 0:
            for boatnumber in range(0,numofpriorlistings):
                boat=(priorlistings.loc[boatnumber])
                priorlistings.loc[boatnumber,"Last Search Date"]=(now.strftime("%d")+'/'+now.strftime("%m")+'/'+now.strftime("%Y"))
                #listingnum is the number of the listing for the boat from the search results
                if listingmum == str(boat["Listing Number"]):
                # We have seen this boat before
                    # check if price has changed and populate latest price change column and lates price columm
                    if listingprice != str(boat['Price']):
                        #we have new price for an old boat
                        priorlistings.loc[boatnumber,'Price']=listingprice
                        priorlistings.loc[boatnumber,'Price Change Date']=(now.strftime("%d")+'/'+now.strftime("%m")+'/'+now.strftime("%Y"))
                        numberofchangedprices=numberofchangedprices+1
                        boatfilename=(str(boat['Listing Number'])+'_'+str(boat['Year'])+'-'+str(boat['Length'])+'-'+boat['Name'].replace(" ","")+'.csv')
                        if os.path.isfile('./'+boatdirectory+"/"+boatfilename):
                            boatdata=pandas.DataFrame()
                            data = pandas.read_csv ('./'+boatdirectory+"/"+boatfilename,sep="|")
                            boatdata = pandas.DataFrame(data)
                            e={}
                            e['Date']=(now.strftime("%d")+'/'+now.strftime("%m")+'/'+now.strftime("%Y"))
                            e['Price']=(listingprice)  
                            boatdata=boatdata.append(e,ignore_index=True)
                            boatdata=pandas.DataFrame(boatdata,index=None)
                            boatdata.to_csv('./'+boatdirectory+"/"+boatfilename,index=False,sep="|")
                        else:
                            print('file not found error, this should not happen')
                        #add mew row to file name
                    boatfound=1
        if boatfound == 0:
            #If boatfound =0 that means we have a listing that didnt exist in out previous summary file. i.e. new listing
            d['Listing Active']='Yes'
            d["Listing Number"]=(productid[counter])
            #date first seen needs to be added to file and then we set it here for new boats
            d["First Seen Date"]=(now.strftime("%d")+'/'+now.strftime("%m")+'/'+now.strftime("%Y"))
            d["Price Change Date"]=(now.strftime("%d")+'/'+now.strftime("%m")+'/'+now.strftime("%Y"))
            d["Last Search Date"]=(now.strftime("%d")+'/'+now.strftime("%m")+'/'+now.strftime("%Y"))
            s=(item.find("div",{"class":"make-model"}))
            if s:
                s=s.text
                start="ft"
                boatname=(s[s.index(start)+len(start):len(s)]).replace(" ","").replace("\n"," ")
                d["Name"]=boatname[8:len(boatname)]
                d['Year']=boatname[0:7].replace(" ","")
            else:
                d['Name']="not found"
            length=(item.find("span",{"class":"length feet"}))
            if length:
                d["Length"]=(item.find("span",{"class":"length feet"})).text.replace("\n","").replace("*","").replace(" ","").replace(",","").replace(u"\xa0","").replace("ft","")
            price=item.find("div",{"class":"price"})
            if price:
                if item.find("div",{"class":"price"}).text.replace("\n","").replace("*","").replace(" ","") == 'Call$(".currNote").hide()':
                    d["Price"]=("Call for current price")
                else:
                    d["Price"]=(item.find("div",{"class":"price"}).text.replace("\n","").replace("*","").replace(" ","").replace("Can$","").replace(u"\xa0","").replace(",",""))
            # setting up old price with same price to keep file structure intact when price chnages
            price=item.find("div",{"class":"price"})
            if price:
                if item.find("div",{"class":"price"}).text.replace("\n","").replace("*","").replace(" ","") == 'Call$(".currNote").hide()':
                    d["Original Price"]=("Call for current price")
                else:
                    d["Original Price"]=(item.find("div",{"class":"price"}).text.replace("\n","").replace("*","").replace(" ","").replace("Can$","").replace(u"\xa0","").replace(",",""))
            location=(item.find("div",{"class":"location"}))
            if location:
                d["Location"]=(item.find("div",{"class":"location"})).text.replace("\n","").replace("*","").replace(" ","")
            broker = (item.find("div",{"class":"broker"}))
            if broker:
                d["Broker"]=(item.find("div",{"class":"broker"})).text.replace("\n","").replace("*","").replace(" ","")
            d["URL"]=(producturl[counter])
            priorlistings=priorlistings.append(d,ignore_index=True)
            boatfilename=d['Listing Number']+'_'+d['Year']+'-'+d['Length']+'-'+d['Name'].replace(" ","")+'.csv'
            # create file and write it (date, price)
            boatdata=pandas.DataFrame()
            e={}
            e['Date']=(now.strftime("%d")+'/'+now.strftime("%m")+'/'+now.strftime("%Y"))
            e['Price']=(d['Price'])
            boatdata=boatdata.append(e,ignore_index=True)
            boatdata=pandas.DataFrame(boatdata,index=None)
            boatdata.to_csv('./'+boatdirectory+'/'+boatfilename,index=False,sep="|")
            numofnewlistings=numofnewlistings+1
        counter = counter+1

#numofactivelistings = priorlistings.shape[0]

if(numofpriorlistings) == 0:
    priorlistings = priorlistings[['Listing Active','Last Search Date','Listing Number','First Seen Date','Year','Name','Length','Price','Original Price','Price Change Date','Location','Broker','URL']]
    priorlistings = pandas.DataFrame(priorlistings,index=None)
else:
    for alllistings in range(0,numofpriorlistings,1):
        allboats=(priorlistings.loc[alllistings])
        boatstillactive=0
        for activelistings in range(0,numofactivelistings,1):
            boatactive=(priorlistings.loc[activelistings])           
            if (str((allboats["Listing Number"]))==str((productidall[activelistings]))):
                #Boat still active
                boatstillactive=1
        if (boatstillactive==0):
            priorlistings.loc[alllistings,'Listing Active']='No'

print("Number of prior listings is "+str(numofpriorlistings))
print("Number of active listings is = "+str(numofactivelistings))
print("Number of new listings is = "+str(numofnewlistings))
print("Number of boats that changed price since last scan = "+str(numberofchangedprices))
priorlistings.to_csv('./'+boatdirectory+'/'+filename+'summary.csv',index=False,sep="|")
# message to be sent 


if n==7:    
    smtpserver=(sys.argv[2])
    fromemail=(sys.argv[3])
    toemail=(sys.argv[4])
    emailuser=(sys.argv[5])
    emailpassword=(sys.argv[6])
    email = smtplib.SMTP(smtpserver, 587)
    email.starttls() 
    email.login(emailuser, emailpassword) 

    subject=('Yachtworld '+filename+' search results.')

    msg=MIMEMultipart()
    msg["From"] = fromemail
    msg['To'] = toemail
    msg["Subject"]=subject
    message = ("Number of active listings is = "+str(numofactivelistings)+"\n"+"Number of prior listings is "+str(numofpriorlistings)+"\n"+"Number of boats that changed price since last scan = "+str(numberofchangedprices)+"\n"+("Number of new listings is = "+str(numofnewlistings)))
    msg.attach(MIMEText(message, 'plain'))
    text=msg.as_string()  
    email.sendmail(fromemail, toemail, text) 
  
# terminating the session 
