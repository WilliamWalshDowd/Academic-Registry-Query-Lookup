import json
import timeit
import sys
sys.path.insert(0, '..')
from outputDataFunctions import *
from transformers import pipeline

COURSEINFOHEADERS = ["Overview", "Awards", "Number of Places", "Next Intake", "Course Coordinator", "Course Director", "Admission Requirements", "Closing Date", "Course Fees"]

#---------------load course data---------------------
file = open('../DataFiles/courseData.json', encoding="utf8")
courseData = json.load(file)

#---------------Roberta QA model---------------------
def getQAOutput(nlp, question, context):
    QA_input = {
        'question': question,
        'context': context
    }
    res = nlp(QA_input)
    return res

#---------------Name Identifier----------------------
def get_topics(input, labels):
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    output = classifier(input, labels)
    formatedOutput = []
    for i in range(len(labels)):
        formatedOutput.append(output['labels'][i] + ': ' + str(round(output['scores'][i]*100, 3)) + "%")
    return formatedOutput

#---------------Header List Find---------------------
def findHeaderList(sheet):
    distinct = []
    for key in sheet.keys():
        distinct.append(key)
    return distinct

#----------------------------------------------------
def courseDataNames(data):
    list = []
    for i in data:
        list.append(i['Name'])
    return list

if __name__ == "__main__":
    while True:
        print("Ask about courses")
        query = input('>')
        start = timeit.default_timer()
        print("----------------Names---------------------")
        names = get_topics(query, courseDataNames(courseData))
        for values in names:
            print(values)
        #layer 1 best result key
        topName = (str(names[0]).split(":"))[0]
        topSheet = {}
        for i in courseData:
            if i['Name'] == topName:
                topSheet = i

        print("----------------Headings---------------------")
        headings = get_topics(query, findHeaderList(topSheet))
        for n in headings:
            print(n)
        TopHeading = (str(headings[0]).split(":"))[0]

        print("---------------Course output-------------")
        for i in courseData:
            if i['Name'] == topName:
                try:
                    print(i[TopHeading])
                    print("Here is the Course page for " + topName + i['Link'])
                except:
                    print("No " + TopHeading + " data found in file for " + topName)
                    print("Here is the Course page for " + topName + i['Link'])
                
        stop = timeit.default_timer()
        print("\n" + "Time taken: " + str(round((stop-start), 1)) + " seconds")
        print("-------------------------------------------")