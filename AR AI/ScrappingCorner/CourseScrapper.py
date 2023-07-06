
import json, re
import requests
from bs4 import BeautifulSoup

# escape string to allow json to parse
def escapeString(string):
    step1 = re.sub('\s+',' ', string)
    step2 = re.sub('\"','\\"', step1)
    return step2

# def removeUnicode(string):
#     findCode = re.search("[\\][u][a-zA-Z0-9]{4}", string)
#     if (findCode == None):
#         return string
#     changeVal = findCode.start()
#     newVal = chr(changeVal)
#     print("before" + string)
#     if newVal == '\\':
#         newVal = '\\\\'
#     step = re.sub("[\\][u][a-zA-Z0-9]{4}", newVal, string, 1)
#     print("after" + step)
#     return removeUnicode(step)

def fixUnicode(string):
    step = re.sub('\u20ac', '€', string)
    step2 = re.sub('\u00a0', ' ', step)
    step3 = re.sub('\u2022', '•', step2)
    step4 = re.sub('\u2019', "'", step3)
    step5 = re.sub('\u2013', '-', step4)
    step6 = re.sub('\u2010', '-', step5)
    return step6

  
# link for extract html data
def getdata(url):
    r = requests.get(url)
    return r.text

# append course data to list
def courseDataToList(soup):
    newList = {}
    for n in soup.findAll('a'):
        name = str(n).split(">", 1)[1][:-4]
        link = "https://www.tcd.ie" + str(n).split('"', 2)[1]
        newList.update({name:link})
    return(newList)

def getNthTag(tag, soup, index):
    for n,item in enumerate(soup.findAll(tag)):
        if n == index:
            return item

def coursePageToList(soup):
    newList = {}
    #course summary
    val = soup.find('div', class_ = "course-section course-section--summary")
    allPs = ""
    for n in val.findAll('p'):
        allPs = allPs + n.getText()
    newList.update({"Overview":(escapeString(allPs))})
    # for n in val:
    #     nextH = n.findNext('h2')
    #     if nextH != None:
    #         p = n.findNext('p')
    #         newList.update({nextH.getText():escapeString(p.getText())})
    #video link
    step3 = soup.find('iframe', class_ = "embed-responsive-item")
    if step3 != None:
        newList.update({"Video":step3['src']})
    #course details
    step4 = soup.find('div', class_ = "col-sm-12 course-details")
    if step4 != None:
        #print("found div")
        courseDetails = ""
        currentH4 = ""
        for idx,n in enumerate(step4.find_all()):
            #print(str(n))
            if ('<h4>' in str(n)):
                #print("found H")
                if currentH4 != "":
                    newList.update({currentH4:(courseDetails)})
                    #print(currentH4 + ": " + courseDetails)
                    courseDetails = ""
                currentH4 = n.getText()
            elif (('<p>' in str(n))or('<span>' in str(n)))and(idx != 0):
                if courseDetails != "":
                    courseDetails = courseDetails + ", " + n.getText()
                else:
                    courseDetails = n.getText()

    #Course Options
    courseOptionsList = []
    step8 = soup.find('div', class_ = "course-tab course-tab--options")
    if step8 != None:
        for n in step8.findAll('a'):
            courseOptionsList.append(escapeString(n.getText()))
        newList.update({"Course Options":courseOptionsList})
    #Admission Requirements
    step9 = soup.find('div', class_ = "container course-fees-wrapper")
    for n in step9:
        nextH = n.findNext('h2')
        if nextH != None:
            p = n.findNext('p')
            newList.update({nextH.getText():(escapeString(p.getText()))})
    #print(newList)

    return newList

# save list to json
def saveToJSON(list, path):
    jsonObject = json.dumps(list, indent=4)
    with open(path, "w", encoding="utf-8") as outfile:
        outfile.write(jsonObject)

if __name__ == "__main__":
    # generates a list of all the courses and there respective links from the search website
    htmlDataPageList = []
    for n in range(24):
        link = 'https://www.tcd.ie/courses/search/?page=' + str(n)
        htmldata = getdata(str(link))
        htmlDataPageList.append(BeautifulSoup(htmldata, 'html.parser').find('div', class_ = 'course-listing-row'))
    linkList = {}
    for soup in htmlDataPageList:
        linkList.update(courseDataToList(soup))
    #print(json.dumps(linkList, indent=3))
    #saveToJSON(linkList, path) # saves list to json file (address of file is not set properly so change to your required path)

    #generate json for all course data found on wepages using linklist made above
    coursePageList = []
    for name,link in linkList.items():
        htmldata = getdata(str(link))
        soup = BeautifulSoup(htmldata, 'html.parser')
        print("checking: " + name + " at " + link)
        val = coursePageToList(soup)
        val.update({"Name":name})
        coursePageList.append(val)

    print(str(len(coursePageList)) + " / " + str(len(linkList)))

    saveToJSON(coursePageList, r"C:\Users\Student.ADMINTR-9FE62E6.000\Documents\AR AI\courseData.json")