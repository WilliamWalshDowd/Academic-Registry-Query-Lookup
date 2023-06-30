
import json, re
import requests
import os.path
from bs4 import BeautifulSoup


# escape string to allow json to parse
def escapeString(string):
    step1 = re.sub('\s+',' ', string)
    step2 = re.sub('\"','\\"', step1)
    return step2
  
# link for extract html data 
def getdata(url): 
    r = requests.get(url) 
    return r.text 

htmldata = getdata("https://www.tcd.ie/academicregistry/fees-and-payments/applicants/how-do-I-pay/")
soup = BeautifulSoup(htmldata, 'html.parser')
data = ''
# for data in soup.find_all("h2"):
#     print(data.get_text())

table = soup.find('div', attrs = {'id':'main-content'})

deadSize = 3
topLoop = 5
loops = [0, 0, 0, 0, 0]

JsonString = "{"

for n in range(deadSize):
    table = table.findNext("h2")

for n in range(topLoop):
    table = table.findNext("h2")
    print("h2 " + table.get_text() + "===================================================================================================================================")
    JsonString += '"' + escapeString(table.get_text()) + '"' + ":["

    if loops[n] != 0:
        for i in range(loops[n]):
            table = table.findNext("h3")
            #print("h3     " + table.get_text() + "-----------------------------------------------------------------------------------------------------------------------------------")
            JsonString += '{"Title" : "' + escapeString(str(table.get_text())) + '",'

            table = table.findNext("div")
            #print("p          " + table.get_text())
            JsonString += '"Content" : "' + escapeString(str(table.get_text())) + '"}'
            if i != loops[n]-1:
                JsonString += ','
            #print("-----------------------------------------------------------------------------------------------------------------------------------")
    else:
        #print("h3     " + table.get_text() + "-----------------------------------------------------------------------------------------------------------------------------------")
        JsonString += '{"Title" : "' + escapeString(str(table.get_text())) + '",'

        table = table.findNext("div")
        #print("p          " + table.get_text())
        JsonString += '"Content" : "' + escapeString(str(table.get_text()))  + '"}'
        #print("-----------------------------------------------------------------------------------------------------------------------------------")
        
    if n == topLoop-1:
        JsonString += "]"
    else:
        JsonString += "],"
    #print("===================================================================================================================================")

JsonString += "}"

JsonObject = json.loads(JsonString)

object = json.dumps(JsonObject, indent=4)

print(object)

with open("ScrappyOutput.json", "w") as outfile:
    outfile.write(object)