import json
import timeit
import sys

from sentence_transformers import SentenceTransformer, util
sys.path.insert(0, '..')
from outputDataFunctions import *
from transformers import pipeline

#---------------Data loader--------------------------
def loadData(fileName):
    try:
        file = open('fileName', encoding="utf8")
    except:
        file = open('./DataFiles/' + fileName, encoding="utf8")
    generalData = json.load(file)
    return generalData

#---------------Label loader-------------------------
def getSheetLabels(generalData):
    justSheets = compileSheetsToList(generalData)
    return justSheets

#---------------Model Loader-------------------------
def loadNLP(model_name):
    nlp = pipeline('question-answering', model=model_name, tokenizer=model_name)
    return nlp

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

#---------------Get course data names----------------
def courseDataNames(data):
    list = []
    for i in data:
        list.append(i['Name'])
    return list

#---------------General query search-----------------
def generalSearch(query):
    generalData = loadData('AcademicRegData.json')
    justSheets = getSheetLabels(generalData)
    #-------------------------------General-----------------------------------------
    printDataTitle(generalData)
    start = timeit.default_timer()
    print("----------------BERT output----------------")
    sheetValues = {}
    barInterable = 0
    labelCount = getAmountOfLabels(generalData)
    printProgressBar(barInterable, labelCount, prefix = 'Progress:', suffix = 'Complete', length = 50)
    nlp = loadNLP("deepset/tinyroberta-squad2")
    startLoop = timeit.default_timer()
    for sheet in justSheets:
        rawContent = sheet['Title'] + " " + sheet['Content']
        modelOutput = getQAOutput(nlp, query, rawContent)
        sheetValues.update({str(sheet['Title']) + " : " + str(getSentenceFromQuote(modelOutput['answer'], rawContent)) : (modelOutput['score'])})
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

    sentences2 = makeTitleList(generalData)

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
        iterable += 1

    print("---------------Sentence output-------------")
    highestSheetVal = max(sheetValues.values())
    highestSheetAnswer = (list(sheetValues.keys())[list(sheetValues.values()).index(highestSheetVal)])
    print(str(highestSheetAnswer) + " : score : " + str(highestSheetVal))

    stop = timeit.default_timer()
    print("\n" + "Time taken: " + str(round((stop-start), 1)) + " seconds")
    print("-------------------------------------------")
    return (str(highestSheetAnswer) + " : score : " + str(highestSheetVal)) 

#---------------Course specific search---------------
def courseSearch(query):
    courseData = loadData('courseData.json')
    #-------------------------------Course------------------------------------------
    print("-------------------------------------------")
    start = timeit.default_timer()
    print("----------------Names---------------------")

    # -----using slow but accurate name identifier-------
    # names = get_topics(query, courseDataNames(courseData))
    # for values in names:
    #     print(values)
    # #layer 1 best result key
    # topName = (str(names[0]).split(":"))[0]
    # topSheet = {}
    # for i in courseData:
    #     if i['Name'] == topName:
    #         topSheet = i

    # -----very fast but more prone to error at large inputs name identifier-------
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    # Two lists of sentences
    sentences1 = []
    sentences2 = []
    for i in courseDataNames(courseData):
        sentences1.append(query)
        sentences2.append(i.lower)
    #Compute embedding for both lists
    embeddings1 = model.encode(sentences1, convert_to_tensor=True)
    embeddings2 = model.encode(sentences2, convert_to_tensor=True)
    #Compute cosine-similarities
    cosine_scores = util.cos_sim(embeddings1, embeddings2)
    #Offset the pairs with similarity score^2
    scoreList = {}
    iterable = 0
    for value in courseDataNames(courseData):
        score = (cosine_scores[iterable][iterable])
        scoreList.update({value:score})
        iterable += 1
    
    scoreList = dict(sorted(scoreList.items(), key=lambda x:x[1], reverse=True))
    for key, value in scoreList.items():
        print(str(key) + " : " + str(value))
    
    topName = tuple(scoreList.items())[0][0]
    print(topName)
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

#---------------Country Info search------------------
def countrySearch(query):
    countryData = loadData('CountryData.json')
    print("-------------------------------------------")
    start = timeit.default_timer()
    print("----------------Names---------------------")

    # -----very fast but more prone to error at large inputs name identifier-------
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    # Two lists of sentences
    sentences1 = []
    sentences2 = []
    for i in countryData.keys():
        sentences1.append(query.lower())
        sentences2.append(i.lower())
        #print(i.lower())

    #Compute embedding for both lists
    embeddings1 = model.encode(sentences1, convert_to_tensor=True)
    embeddings2 = model.encode(sentences2, convert_to_tensor=True)
    #Compute cosine-similarities
    cosine_scores = util.cos_sim(embeddings1, embeddings2)
    #Offset the pairs with similarity score^2
    scoreList = {}
    iterable = 0
    for value in countryData.keys():
        score = (cosine_scores[iterable][iterable])
        scoreList.update({value:score})
        iterable += 1
    
    scoreList = dict(sorted(scoreList.items(), key=lambda x:x[1], reverse=True))
    for key, value in scoreList.items():
        print(str(key) + " : " + str(value))
    
    topName = tuple(scoreList.items())[0][0]
    print(topName)
    topSheet = {}
    for key, val in countryData.items():
        if key == topName:
            topSheet = val

    print("----------------Headings---------------------")
    headings = get_topics(query, findHeaderList(topSheet))
    for n in headings:
        print(n)
    TopHeading = (str(headings[0]).split(":"))[0]

    outputString = ""
    print("---------------Course output-------------")
    for key, val in countryData.items():
        if key == topName:
            try:
                outputString = (val[TopHeading]) + "\n"
                outputString += ("Here is the Course page for " + topName + ": " + val['Link'])
            except:
                outputString = ("No " + TopHeading + " data found in file for " + topName) + "\n"
                outputString += ("Here is the Course page for " + topName + ": " + val['Link'])
            
    stop = timeit.default_timer()
    print("\n" + "Time taken: " + str(round((stop-start), 1)) + " seconds")
    print("-------------------------------------------")
    return outputString

#---------------Terminal interaction function--------
def main():
    while True:
        print("Do you want to ask about specific courses, specific countries or general information")
        queryFilter1 = input('>')
        filter1 = get_topics(queryFilter1, ['General', 'Course', 'Country'])
        #print(filter1)
        if (str(filter1[0]).split(":"))[0] == 'General':
            print("-------------------------------------------")
            print("Ask a Query about general information (Example: 'Give me information about CAO Applications')")
            query = input('>')
            print(generalSearch(query))
        elif (str(filter1[0]).split(":"))[0] == 'Course':
            print("-------------------------------------------")
            print("Ask a Query about Courses (Example: 'What are the admission requirements for Economics?')")
            query = input('>')
            print(courseSearch(query))
        else:
            print("-------------------------------------------")
            print("Ask a Query about Country requirements (Example: 'What are the Undergraduate requirements for Algeria?')")
            query = input('>')
            print(countrySearch(query))

if __name__ == "__main__":
    main()