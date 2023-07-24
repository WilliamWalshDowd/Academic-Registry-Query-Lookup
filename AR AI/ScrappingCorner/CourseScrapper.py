
import json, re
import requests
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

def customTagSelector(tag):
    return tag.name == "p" or tag.name == "span" or tag.name == "h2" or tag.name == "h3" or tag.name == "font" or tag.name == "li" or tag.name == "#"

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

    #video link
    step3 = soup.find('iframe', class_ = "embed-responsive-item")
    if step3 != None:
        watchLink = step3['src'].replace("embed/", "watch?v=")
        newList.update({"Video":watchLink})

    #course details
    step4 = soup.find('div', class_ = "col-sm-12 course-details")
    if step4 != None:
        #print("found div-------------------------------------------------------------")
        courseDetails = ""
        currentH4 = ""
        for idx,n in enumerate(step4.find_all()):
            #print(str(n))
            if ('<h4>' in str(n)):
                if currentH4 != "":
                    newList.update({currentH4:(courseDetails)})
                    courseDetails = ""
                #print("     " + str(n))
                currentH4 = n.getText()
            elif (('<p>' in str(n))or('<span>' in str(n)))and(idx != 0):
                #print("     " + n.getText())
                if (courseDetails != "") and (n.getText() != courseDetails):
                    courseDetails = courseDetails + ", " + n.getText()
                elif(n.getText() != ""):
                    courseDetails = n.getText()
                #print(courseDetails)
        newList.update({currentH4:(courseDetails)})

    #Course Options
    courseOptionsList = {}
    courseSoup = soup.find('div', class_ = "course-tab course-tab--options")
    if courseSoup != None:
        for n in courseSoup.findAll('a'):
            courseOptionsList.update({escapeString(n.getText()):n.get("href")})
        newList.update({"Course Options":courseOptionsList})

    #Admission Requirements older version
    # step9 = soup.find('div', class_ = "container course-fees-wrapper")
    # if step9 != None:
    #     #print("found div-------------------------------------------------------------")
    #     courseDetails = ""
    #     currentH2 = ""
    #     for idx,n in enumerate(step9.find_all(customTagSelector)):
    #         #print(str(n))
    #         if ('</h2>' in str(n)):
    #             if currentH2 != "":
    #                 if courseDetails == "":
    #                     courseDetails = "No info on webpage"
    #                 elif courseDetails == "Click here for a full list of undergraduate fees.":
    #                     courseDetails = courseDetails + " https://www.tcd.ie/academicregistry/fees-and-payments/"
    #                 newList.update({currentH2:(courseDetails)})
    #                 courseDetails = ""
    #             #print("     " + str(n))
    #             currentH2 = n.getText()
    #         elif (idx != 0):
    #             #print("     " + n.getText())
    #             if (courseDetails != "") and (n.getText() != courseDetails):
    #                 courseDetails = courseDetails + ", " + n.getText()
    #             elif(n.getText() != ""):
    #                 courseDetails = n.getText()
    #     if currentH2 != "" and courseDetails != "":
    #         newList.update({currentH2:(courseDetails)})

    #Admission Requirements
    admissionDiv = (soup.find('div', class_ = "container course-fees-wrapper")).find('div', class_ = "course-content-hidden__block")
    if admissionDiv != None:
        admissionContent = ""
        for i in admissionDiv.findAll():
            if '<h2>' not in i.getText():
                if admissionContent != "":
                    admissionContent = admissionContent + "\n" + i.getText()
                else:
                    admissionContent = i.getText() + ": "
        if admissionContent == "":
            admissionContent = "No info on the webpage"
        newList.update({"Admission Requirements":(admissionContent)})
    else:
        newList.update({"Admission Requirements":("No info on the webpage")})

    #Fee and Payments
    FeesDiv = (soup.find('div', class_ = "container course-fees-wrapper")).findAll('div', class_ = "col-sm-12")
    if FeesDiv != None:
        feesContent = ""
        for i in FeesDiv[-1].findAll():
            if '<h2>' not in i.getText():
                if feesContent != "":
                    feesContent = feesContent + "\n" + i.getText()
                else:
                    feesContent = i.getText() + ": "
        if feesContent == "":
            feesContent = "No info on the webpage"
        newList.update({"Fees and Payments":(feesContent + ". Link to fees page https://www.tcd.ie/academicregistry/fees-and-payments/")})
    else:
        newList.update({"Fees and Payments":("No info on the webpage")})

    #School Website link
    schoolDiv = (soup.find('div', class_ = "course-tab course-tab--get-in-touch"))
    if schoolDiv != None:
        lastElement = ""
        for i in schoolDiv.findAll():
            if "Website" in lastElement:
                #print(i.getText())
                newList.update({"School Webpage":"https://" + re.sub(' | ','', i.getText())})
            lastElement = i.getText()

    return newList

# save list to json
def saveToJSON(list, path):
    jsonObject = json.dumps(list, indent=4, ensure_ascii=False)
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
    #sort alphabeticaly
    myKeys = list(linkList.keys())
    myKeys.sort()
    linkList = {i: linkList[i] for i in myKeys}
    #saveToJSON(linkList, path) # saves list to json file (address of file is not set properly so change to your required path)

    # generate json for all course data found on wepages using linklist made above
    coursePageList = []
    for name,link in linkList.items():
        htmldata = getdata(str(link))
        soup = BeautifulSoup(htmldata, 'html.parser')
        print("checking: " + name + " at " + link)
        val = coursePageToList(soup)
        val.update({"Name":name})
        val.update({"Link":link})
        coursePageList.append(val)

    print(str(len(coursePageList)) + " / " + str(len(linkList)))

    saveToJSON(coursePageList, "../DataFiles/courseData.json")