import json
import os
import webbrowser
import timeit
from multiprocessing import Process
import multiprocessing
import sys
sys.path.insert(0, '..')
from outputDataFunctions import *
from transformers import pipeline

COURSEINFOHEADERS = ["Overview", "Awards", "Number of Places", "Next Intake", "Course Coordinator", "Course Director", "Admission Requirements", "Closing Date", "Course Fees"]

#--------------Test data loader-----------------------
file = open('DataFiles/testdata.json', encoding="utf8")
data = json.load(file)
file = open('DataFiles/courseData.json', encoding="utf8")
courseData = json.load(file)

#---------------Label loader--------------------------
print("---------------loading data-------------------")
justSheets = compileSheetsToList(data)
print("----------------------------------------------") 

#---------------Model Loader-------------------------
model_name = "deepset/bert-large-uncased-whole-word-masking-squad2"
nlp = pipeline('question-answering', model=model_name, tokenizer=model_name)

#---------------Roberta QA model------------------
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
        print("Do you want to ask about specific courses or general content")
        queryFilter1 = input('>')
        filter1 = get_topics(queryFilter1, ['General query', 'Course query'])
        if (str(filter1[0]).split(":"))[0] == 'General query':
            #-------------------------------General-----------------------------------------
            printDataTitle(data)
            print("Ask a Query about general information (Example: 'Give me information about CAO Applications')")
            query = input('>')
            start = timeit.default_timer()
            print("----------------BERT output----------------")
            sheetValues = {}
            barInterable = 0
            labelCount = getAmountOfLabels(data)
            printProgressBar(barInterable, labelCount, prefix = 'Progress:', suffix = 'Complete', length = 50)

            startLoop = timeit.default_timer()
            for sheet in justSheets:
                rawContent = sheet['Title'] + ": " + sheet['Content']
                modelOutput = getQAOutput(nlp, query, rawContent)
                sheetValues.update({str(sheet['Title']) + " : " + str(getSentenceFromQuote(modelOutput['answer'], rawContent)) : modelOutput['score']})
                # print(str(sheet['Title']) + " : " + str(getSentenceFromQuote(modelOutput['answer'], rawContent)) + "(" + str(modelOutput['score']) + ")")
                stopLoop = timeit.default_timer()
                percentagePerSecond = round((1/(stopLoop-startLoop))*((barInterable+1)/len(justSheets))*100, 2)
                estimatedFinishTime = round((100-((barInterable+1)/len(justSheets))*100)/percentagePerSecond, 1)
                printProgressBar(barInterable + 1, labelCount, prefix = 'Progress:', suffix = 'Complete (' + str(percentagePerSecond) + "% per second, time left " + str(estimatedFinishTime) + " seconds ", length = 50)
                barInterable += 1

            print("---------------sentence output-------------")
            highestSheetVal = 0
            highestSheetAnswer = []
            secondHighestSheetAnswer = []
            secondHighestSheetVal = 0
            for name, value in sheetValues.items():
                if value >= highestSheetVal:
                    secondHighestSheetVal = highestSheetVal
                    highestSheetVal = value
                    secondHighestSheetAnswer = highestSheetAnswer
                    highestSheetAnswer = name
            print(str(highestSheetAnswer) + " : score : " + str(highestSheetVal))
            print(str(secondHighestSheetAnswer) + " : score : " + str(secondHighestSheetVal))

            stop = timeit.default_timer()
            print("\n" + "Time taken: " + str(round((stop-start), 1)) + " seconds")

            print("-------------------------------------------")
        else:
            #-------------------------------Course------------------------------------------
            print("Ask a Query about Courses (Example: 'what are the admission requirements for Economics?')")
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