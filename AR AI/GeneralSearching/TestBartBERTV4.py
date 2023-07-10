#Seperate BERT QA model value comparison
import json
import os
import webbrowser
import timeit
from multiprocessing import Process
import multiprocessing
from outputDataFunctions import *
from transformers import pipeline

#--------------Test data loader-----------------------
file = open('../DataFiles/testdata.json')
data = json.load(file)

#---------------Label loader--------------------------
print("---------------loading data-------------------")
justSheets = compileSheetsToList(data)
printDataTitle(data)
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

#-------------------------------------------Input output test--------------------------------------------------
if __name__ == '__main__':
    while True:
        print("Ask a Query")
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