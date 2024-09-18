from distutils.command.check import HAS_DOCUTILS
from re import search
import requests
import pandas as pd
import json
import ipaddress
import socket
from urllib3.exceptions import InsecureRequestWarning
import getpass


# Checks if the value taken from the description column is an IP or a hostname
def checkIfIP(host):
    try:
        ip = ipaddress.ip_address(host)
        print('%s is a correct IP%s address.' % (ip, ip.version))
        return ip
    except ValueError:
        print('Hostname entered, finding IP...')
        try:
            returnedIP = socket.gethostbyname(host)
            return returnedIP
        except socket.gaierror:
            return host
    except:
        print('Usage : %s  ip' % host)
        

api_authorization = getpass.getpass(prompt="Enter API key for Xpanse v2") 


INCREMENT = 100
search_from = 0
search_to = INCREMENT

listIssue = []


# Call the get_incidents API endpoints to determine the total number of active incidents
headers = {'Authorization': api_authorization,
                'x-xdr-auth-id':'1',
                'Accept':'application/json',
                'Content-Type':'application/json'}
myobj = {"request_data":{}}


apiURL = "REPLACE WITH URL"
issueResponse = requests.post(apiURL, headers = headers, json = myobj)
print(issueResponse)
issueData = issueResponse.text

dataframe1 = pd.read_json(issueData)
print(dataframe1)
totalIssues = int(dataframe1['reply']['total_count'])
print(totalIssues)




# download all the Xpanse incidents in increments of 100 until the total # of issues is reached
while search_from < totalIssues:
    headers = {'Authorization': api_authorization,
                'x-xdr-auth-id':'1',
                'Accept':'application/json',
                'Content-Type':'application/json'}
    myobj = {"request_data":{
        "search_from":search_from,
        "search_to":search_to
    }
    }

    issueResponse = requests.post('https://api-ndgov-xpanse.crtx.us.paloaltonetworks.com/public_api/v1/incidents/get_incidents', headers = headers, json = myobj)
    issueData = issueResponse.text
    print("Issue Data")
    print(issueData)

    dataframe1 = pd.read_json(issueData)
    newDF = dataframe1['reply']['incidents']
    listIssue += newDF
    search_from += INCREMENT
    search_to += INCREMENT



# write incidents to file
with open('issue.txt', 'w') as file:
    json.dump(listIssue, file)


dataframe1 = pd.read_json(".\\issue.txt")

dataframe1.to_csv('high-criticalXpanseIssues.csv',index=None)





# get the hostnames/IPs from the description column
csvFile = 'high-criticalXpanseIssues.csv'

data = pd.read_csv(csvFile)

hosts = data['description'].tolist()
newHosts = []
for i in hosts:
    string = (i.split('at ',1)[1])
    newHosts.append(string.split(':',1)[0])


ipList = []
for host in newHosts:
    ipList.append(checkIfIP(host))



data = pd.read_csv(csvFile)
df = pd.DataFrame(data)

df.insert(0, 'Host/IP', newHosts)
df.insert(1, 'IP', ipList)

newCSV = df.to_csv('xpanseIssuesWithHostsandIPs.csv')


