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
compiledContent = compileSheetContentToList(data)
print(compiledContent)
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
while True:
    print("Ask a Query on Aplications, Entry requirenments or alternate paths to Trinity")
    query = input('>')
    start = timeit.default_timer()
    print("----------------BERT output----------------")
    modelOutput = getQAOutput(nlp, query, compiledContent)
    print(modelOutput)

    print("---------------sentence output-------------")
    print(getSentenceFromQuote(modelOutput['answer'], compiledContent))
    stop = timeit.default_timer()
    print("Time taken" + stop-start)
    print("-------------------------------------------")