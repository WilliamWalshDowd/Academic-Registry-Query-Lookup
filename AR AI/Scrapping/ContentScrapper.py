
import json, re
import requests
from bs4 import BeautifulSoup


# escape string to allow json to parse
def escapeString(string):
    step1 = re.sub('\s+',' ', string)
    step2 = re.sub('\n','', step1)
    return step2
  
# link for extract html data 
def getdata(url): 
    r = requests.get(url) 
    return r.text 

def getDataJson(link):

    htmldata = getdata(link)
    soup = BeautifulSoup(htmldata, 'html.parser')

    newList = {}
    
    step4 = soup.find('div', class_ = "main-content")
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

        # add link to list
        newList.update({'link':link})

        finalList = {}
        for key,value in newList.items():
            #print(str(key) + ":" + str(value))
            for i in headerlist:
                #print("HEAD     " + str(i))
                #print("VALUE    " + str(key))
                if str(key).replace(' ', '') in str(i).replace(' ',''):
                    #print("TRUE")
                    finalList.update({key:value})

    return finalList

def saveToJSON(list, path):
    jsonObject = json.dumps(list, indent=4, ensure_ascii=False)
    with open(path, "w", encoding="utf-8") as outfile:
        outfile.write(jsonObject)

def makeSitemapJson(sitemap):
    htmldata = getdata(sitemap)
    soup = BeautifulSoup(htmldata, 'html.parser')
    sitemap  = soup.find('div', class_ = 'section-sitemap')

    sitemapPages = {}
    for elements in sitemap.findAll('a'):
        sitemapPages.update({elements.getText():elements.get('href')})

    jsonList = []
    for name, link in sitemapPages.items():
        try:
            pageFiles = getDataJson(link)
        except:
            try:
                pageFiles = getDataJson('https:' + link)
            except:
                print('Invalid/Locked URL: ' + link)
            
            if pageFiles != {}:
                for i,j in pageFiles.items():
                    if (str(i).replace(' ', '') != "") and (str(j).replace(' ', '') != ""):
                        #print('i     ' + str(i))
                        #print('j     ' + str(j))
                        jsonList.append({'Title':name + ' - ' + str(i), 'Content':str(j), 'Link':str('https:' + link)})
                        #print(jsonList)
    return jsonList

if __name__ == "__main__":
    allJsons = {}
    allJsons.update({'Academic Registry':makeSitemapJson('https://www.tcd.ie/academicregistry/sitemap/')})
    allJsons.update({'Study':makeSitemapJson('https://www.tcd.ie/study/sitemap/')})

    allJsons.update({'Sport':makeSitemapJson('https://www.tcd.ie/Sport/sitemap/')})
    

    saveToJSON(allJsons, '../DataFiles/AcademicRegData.json')