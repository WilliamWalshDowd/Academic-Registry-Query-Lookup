#Seperate BERT QA model value comparison
import json
import os
import webbrowser
import timeit
from outputDataFunctions import *
from transformers import pipeline

#--------------Test data loader-----------------------
file = open('testdata.json')
data = json.load(file)

#---------------Label loader--------------------------
print("---------------loading data-------------------")
justSheets = compileSheetsToList(data)
printDataTitle(data)
print("----------------------------------------------") 

#---------------Model Loader-------------------------
model_name = "deepset/tinyroberta-squad2"
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
while True:
    print("Ask a Query on Aplications, Entry requirenments or alternate paths to Trinity")
    query = input('>')
    start = timeit.default_timer()
    print("----------------BERT output----------------")
    sheetValues = {}
    barInterable = 0
    labelCount = getAmountOfLabels(data)
    printProgressBar(barInterable, labelCount, prefix = 'Progress:', suffix = 'Complete', length = 50)

    for sheet in justSheets:
        rawContent = sheet['Title'] + "\n" + sheet['Content']
        modelOutput = getQAOutput(nlp, query, rawContent)
        sheetValues.update({str(sheet['Title']) + " : " + str(getSentenceFromQuote(modelOutput['answer'], rawContent)) : modelOutput['score']})
        #print(str(sheet['Title']) + " : " + str(getSentenceFromQuote(modelOutput['answer'], rawContent)) + "(" + str(modelOutput['score']) + ")")
        printProgressBar(barInterable + 1, labelCount, prefix = 'Progress:', suffix = 'Complete', length = 50)
        barInterable += 1

    print("---------------sentence output-------------")
    highestSheetVal = 0
    highestSheetAnswer = []
    for name, value in sheetValues.items():
        if value >= highestSheetVal:
            highestSheetVal = value
            highestSheetAnswer = name
    print(highestSheetAnswer)

    stop = timeit.default_timer()
    print("\n" + "Time taken: " + str(stop-start) + " seconds")

    print("-------------------------------------------")