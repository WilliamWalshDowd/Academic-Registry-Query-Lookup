
import json, re
import requests 
from bs4 import BeautifulSoup

from outputDataFunctions import *
  
# link for extract html data 
def getdata(url): 
    r = requests.get(url) 
    return r.text 
  
htmldata = getdata("https://www.tcd.ie/academicregistry/faq/") 
soup = BeautifulSoup(htmldata, 'html.parser') 
data = '' 
# for data in soup.find_all("h2"):
#     print(data.get_text())

table = soup.find('div', attrs = {'id':'main-content'})

topLoop = 8
loops = [5, 14, 10, 6, 0, 9, 0, 5]

JsonString = "{"

for n in range(topLoop):
        table = table.findNext("h2")
        #print("h2 " + table.get_text() + "===================================================================================================================================")
        JsonString +=  '"' + escapeString(table.get_text()) + '"' + ":["

        if loops[n] != 0:
            for i in range(loops[n]):
                table = table.findNext("h3")
                #print("h3     " + table.get_text() + "-----------------------------------------------------------------------------------------------------------------------------------")
                JsonString += '{"Title" : "' + escapeString(str(table.get_text())) + '",'

                table = table.findNext("p")
                #print("p          " + table.get_text())
                JsonString += '"Content" : "' + escapeString(str(table.get_text())) + '"}'
                if i != loops[n]-1:
                    JsonString += ','
                #print("-----------------------------------------------------------------------------------------------------------------------------------")
        else:
            #print("h3     " + table.get_text() + "-----------------------------------------------------------------------------------------------------------------------------------")
            JsonString += '{"Title" : "' + escapeString(str(table.get_text())) + '",'

            table = table.findNext("p")
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

# with open("ScrappyOutput.json", "w") as outfile:
#      outfile.write(object)