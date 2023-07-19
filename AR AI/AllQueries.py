import json
import timeit
#from multiprocessing import Process
import sys

from sentence_transformers import SentenceTransformer, util
sys.path.insert(0, '..')
from outputDataFunctions import *
from transformers import pipeline


# default for testing, headers are decided based on which course is selected
COURSEINFOHEADERS = ["Overview", "Awards", "Number of Places", "Next Intake", "Course Coordinator", "Course Director", "Admission Requirements", "Closing Date", "Course Fees"]

#--------------Test data loader-----------------------
def loadTestData():
    file = open('DataFiles/testdata.json', encoding="utf8")
    generalData = json.load(file)
    return generalData

def loadCourseData():
    file = open('DataFiles/courseData.json', encoding="utf8")
    courseData = json.load(file)
    return courseData

#---------------Label loader--------------------------
def getSheetLabels(generalData):
    justSheets = compileSheetsToList(generalData)
    return justSheets

#---------------Model Loader-------------------------
def loadNLP(model_name):
    nlp = pipeline('question-answering', model=model_name, tokenizer=model_name)
    return nlp

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

def generalSearch(query):
    generalData = loadTestData()
    justSheets = getSheetLabels(generalData)
    #-------------------------------General-----------------------------------------
    printDataTitle(generalData)
    start = timeit.default_timer()
    print("----------------BERT output----------------")
    sheetValues = {}
    barInterable = 0
    labelCount = getAmountOfLabels(generalData)
    printProgressBar(barInterable, labelCount, prefix = 'Progress:', suffix = 'Complete', length = 50)

    startLoop = timeit.default_timer()
    for sheet in justSheets:
        rawContent = sheet['Title'] + " " + sheet['Content']
        modelOutput = getQAOutput(loadNLP("deepset/xlm-roberta-large-squad2"), query, rawContent)
        sheetValues.update({str(sheet['Title']) + " : " + str(getSentenceFromQuote(modelOutput['answer'], rawContent)) : (modelOutput['score'])})
        # print(str(sheet['Title']) + " : " + str(getSentenceFromQuote(modelOutput['answer'], rawContent)) + "(" + str(modelOutput['score']) + ")")
        stopLoop = timeit.default_timer()
        percentagePerSecond = round((1/(stopLoop-startLoop))*((barInterable+1)/len(justSheets))*100, 2)
        estimatedFinishTime = round((100-((barInterable+1)/len(justSheets))*100)/percentagePerSecond, 1)
        printProgressBar(barInterable + 1, labelCount, prefix = 'Progress:', suffix = 'Complete (' + str(percentagePerSecond) + "% per second, time left " + str(estimatedFinishTime) + " seconds ", length = 50)
        barInterable += 1

    print("---------------Similarity------------------")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Two lists of sentences
    sentences1 = []
    for i in makeTitleList(generalData):
        sentences1.append(query)
    #print(len(sentences1))

    sentences2 = makeTitleList(generalData)
    #print(len(sentences2))

    #Compute embedding for both lists
    embeddings1 = model.encode(sentences1, convert_to_tensor=True)
    embeddings2 = model.encode(sentences2, convert_to_tensor=True)

    #Compute cosine-similarities
    cosine_scores = util.cos_sim(embeddings1, embeddings2)

    #Offset the pairs with similarity score^2
    iterable = 0
    for key, value in sheetValues.items():
        score = (cosine_scores[iterable][iterable])
        sheetValues[key] = value*(score*score)
        # print("{} \t {} \t Score: {:.4f}".format(sentences1[iterable], sentences2[iterable], score))
        iterable += 1

    print("---------------Sentence output-------------")
    highestSheetVal = max(sheetValues.values())
    highestSheetAnswer = (list(sheetValues.keys())[list(sheetValues.values()).index(highestSheetVal)])
    print(str(highestSheetAnswer) + " : score : " + str(highestSheetVal))
    #for key, name in sorted(sheetValues.items(), key=lambda x:x[1], reverse=True):
        #print(key + " : " + str(name))

    stop = timeit.default_timer()
    print("\n" + "Time taken: " + str(round((stop-start), 1)) + " seconds")
    print("-------------------------------------------")
    return (str(highestSheetAnswer) + " : score : " + str(highestSheetVal))

def courseSearch(query):
    courseData = loadCourseData()
    #-------------------------------Course------------------------------------------
    print("-------------------------------------------")
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

    outputString = ""
    print("---------------Course output-------------")
    for i in courseData:
        if i['Name'] == topName:
            try:
                outputString = (i[TopHeading]) + "\n"
                outputString += ("Here is the Course page for " + topName + ": " + i['Link'])
            except:
                outputString = ("No " + TopHeading + " data found in file for " + topName) + "\n"
                outputString += ("Here is the Course page for " + topName + ": " + i['Link'])
            
    stop = timeit.default_timer()
    print("\n" + "Time taken: " + str(round((stop-start), 1)) + " seconds")
    print("-------------------------------------------")
    return outputString

def main():
    while True:
        print("Do you want to ask about specific courses or general content")
        queryFilter1 = input('>')
        filter1 = get_topics(queryFilter1, ['General query', 'Course query'])
        if (str(filter1[0]).split(":"))[0] == 'General query':
            print("-------------------------------------------")
            print("Ask a Query about general information (Example: 'Give me information about CAO Applications')")
            query = input('>')
            print(generalSearch(query))
        else:
            print("-------------------------------------------")
            print("Ask a Query about Courses (Example: 'what are the admission requirements for Economics?')")
            query = input('>')
            print(courseSearch(query))

if __name__ == "__main__":
    main()