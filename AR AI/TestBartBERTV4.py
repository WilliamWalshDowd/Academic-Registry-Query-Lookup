import json
import os
import webbrowser
from outputDataFunctions import *
from transformers import pipeline

#--------------Test data loader-----------------------
file = open('testdata.json')
data = json.load(file)

#---------------Label loader--------------------------
print("---------------loading data-------------------")
LABELS = {}
for catagory, value in data.items():
    print("\n" + catagory)
    LABELS[catagory] = []
    for sheet in value:
        print("     " + sheet['Title'])
        LABELS[catagory].append(sheet['Title'])

justSheets = compileSheetsToList(data)
print("----------------------------------------------") 

#---------------Model Loader-------------------------
model_name = "deepset/bert-large-uncased-whole-word-masking-squad2"
nlp = pipeline('question-answering', model=model_name, tokenizer=model_name)

#----------------------------------------------Topic identifier------------------------------------------------
# def get_topics(input, labels):
#     classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
#     output = classifier(input, labels, multi_label=True)
#     formatedOutput = []
#     for i in range(len(labels)):
#         formatedOutput.append(output['labels'][i] + ': ' + str(round(output['scores'][i]*100, 3)) + "%")
    
#     return formatedOutput

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

    print("---------------label output layer 1--------")
    print("----------------BERT output----------------")
    sheetValues = {}
    for sheet in justSheets:
        rawContent = sheet['Content']
        modelOutput = getQAOutput(nlp, query, rawContent)
        sheetValues.update({str(sheet['Title']) + " : " + str(getSentenceFromQuote(modelOutput['answer'], rawContent)) : modelOutput['score']})
        print(str(sheet['Title']) + " : " + str(getSentenceFromQuote(modelOutput['answer'], rawContent)) + "(" + str(modelOutput['score']) + ")")
    print(sheetValues)

    print("---------------sentence output-------------")
    highestSheetVal = 0
    highestSheetAnswer = []
    for name, value in sheetValues.items():
        if value >= highestSheetVal:
            highestSheetVal = value
            highestSheetAnswer = name
    print(highestSheetAnswer)

    print("-------------------------------------------")