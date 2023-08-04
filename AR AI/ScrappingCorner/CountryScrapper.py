import json, re
import requests
from bs4 import BeautifulSoup

def escapeString(string):
    step1 = re.sub('\s+',' ', string)
    step2 = re.sub('\"','\\"', step1)
    return step2

def getdata(url): 
    r = requests.get(url) 
    return r.text 

def getDataJson(link):

    htmldata = getdata(link)
    soup = BeautifulSoup(htmldata, 'html.parser')

    newList = {}
    
    step4 = soup.find_all('div', class_ = "lay-centered width-max")
    step4 = step4[6]
    if step4 != None:
        #print("found div-------------------------------------------------------------")
        details = ""
        currentH3 = ""
        headerlist = []
        for i in step4.find_all('h2'):
            headerlist.append(i.getText())
        for idx,n in enumerate(step4.find_all()):
            if ('<h2>' in str(n)):
                if currentH3 != "":
                    newList.update({escapeString(currentH3):escapeString(details)})
                    details = ""
                #print("     " + str(n))
                currentH3 = n.getText()
            elif ('<p>' in str(n) or '<span>' in str(n) or '<h3>' in str(n) or '</a>' in str(n) or '<li>' in str(n))and(idx != 0):
                #print("     " + n.getText())
                if (details != "") and (n.getText() != details):
                    if ('</a>' in str(n)) and ('<p>' not in str(n)):
                        details = details + n.getText() + ", " + str(n.get("href"))
                    else:
                        details = details + ", " + n.getText()
                elif(n.getText() != ""):
                    if ('</a>' in str(n)) and ('<p>' not in str(n)):
                        details = n.getText() + ', ' + str(n.get("href"))
                    else:
                        details = n.getText()
                #print(details)
        newList.update({escapeString(currentH3):escapeString(details)})

        # remove blank content elements
        for i in list(newList.keys()):
            if newList[i] == '':
                del newList[i]

        # remove content with incorrect data
        for i in list(newList.keys()):
            if i == '' or i[0] == ' ':
                del newList[i]

    return newList

def saveToJSON(list, path):
    jsonObject = json.dumps(list, indent=4, ensure_ascii=False)
    with open(path, "w", encoding="utf-8") as outfile:
        outfile.write(jsonObject)

if __name__ == '__main__':

    countrys = {}
    htmldata = getdata('https://www.tcd.ie/study/country/')
    soup = BeautifulSoup(htmldata, 'html.parser')
    sheet = soup.find_all('ul', class_ = "list-links")
    for sublist in sheet:
        for link in sublist.find_all('a', href=True):
            print(link.getText() + ' https://www.tcd.ie/study/country/' + link['href'])
            countrys.update({link.getText():'https://www.tcd.ie/study/country/' + link['href']})
    
    countryData = {}
    for name, link in countrys.items():
        countryPageData = getDataJson(link)
        countryPageData.update({'Link':link})
        countryData.update({name:countryPageData})
        print(name)


    saveToJSON(countryData, '../DataFiles/CountryData.json') # saves list to json file (address of file is not set properly so change to your required path)