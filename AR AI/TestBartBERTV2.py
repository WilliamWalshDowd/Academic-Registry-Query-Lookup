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
def get_topics(input, labels):
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    output = classifier(input, labels) #multi_label=True
    formatedOutput = []
    for i in range(len(labels)):
        formatedOutput.append(output['labels'][i] + ': ' + str(round(output['scores'][i]*100, 3)) + "%")
        
    return formatedOutput

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

    print("----------------topics---------------------")
    #layer 1
    topics = get_topics(query, makeTitleList(data))
    for values in topics:
        print(values)
    #layer 1 best result key
    topTopicLayer1 = (str(topics[0]).split(":"))[0]

    print("---------------label output layer 1--------")
    print(str(topics[0]))
    rawContent = getOutput(topTopicLayer1, data, LABELS)
    print(rawContent)

    print("----------------BERT output----------------")
    modelOutput = getQAOutput(nlp, query, rawContent)
    print(modelOutput)

    print("---------------sentence output-------------")
    sentenceAnswer = getSentenceFromQuote(modelOutput['answer'], rawContent)
    print(sentenceAnswer)

    print("-------------------------------------------")