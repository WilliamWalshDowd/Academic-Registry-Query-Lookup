import json
import os
import webbrowser
from transformers import pipeline

#--------------Test data loader-----------------------
file = open('../DataFiles/testdata.json')
data = json.load(file)

#---------------Label loader--------------------------
LABELS = {}
print("---------------loading data-------------------")
for catagory, value in data.items():
    print("\n" + catagory)
    LABELS[catagory] = []
    for sheet in value:
        print("     " + sheet['Title'])
        LABELS[catagory].append(sheet['Title'])
print("----------------------------------------------") 

#---------------Model Loader-------------------------
model_name = "deepset/bert-large-uncased-whole-word-masking-squad2"
nlp = pipeline('question-answering', model=model_name, tokenizer=model_name)

#----------------------------------------------Topic identifier------------------------------------------------
def get_topics(input, labels):
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    output = classifier(input, labels, multi_label=True)
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

#----------------------------------------------Topic output lookup---------------------------------------------
def getOutput(title, dataVal):
    for catagory, value in dataVal.items():
        for sheet in value:
            LABELS[catagory].append(sheet['Title'])
            if sheet['Title'] == title:
                return sheet['Content']
    return "No Matching Files In Data"
        
def getSentenceFromQuote(quote, text):
    sentences = []
    for sentence in text.split("."):
        if quote in sentence:
            sentences.append(sentence)
    return sentences

def makeTitleList(catagory, dataVal):
    list = []
    for sheet in dataVal[catagory]:
        list.append(sheet["Title"])
    return list

def getHTMLOutput(title, dataVal):
    for catagory, value in dataVal.items():
        for sheet in value:
            LABELS[catagory].append(sheet['Title'])
            if sheet['Title'] == title:
                return sheet['html']
    return "No Matching Files In Data"


#-------------------------------------------Input output test--------------------------------------------------
while True:
    print("Ask a Query on Aplications, Entry requirenments or alternate paths to Trinity")
    query = input('>')

    print("----------------topics---------------------")
    #layer 1
    topics = get_topics(query, list(LABELS.keys()))
    print(topics)
    #layer 1 best result key
    topTopicLayer1 = (str(topics[0]).split(":"))[0]
    #layer 2
    topics = get_topics(query, makeTitleList(topTopicLayer1, data))
    print(topics)
    #layer 2 best result key
    topTopicLayer2 = (str(topics[0]).split(":"))[0]

    print("---------------label output layer 1--------")
    print(str(topics[0]))
    rawContent = getOutput(topTopicLayer2, data)
    print(rawContent)

    print("----------------BERT output----------------")
    modelOutput = getQAOutput(nlp, query, rawContent)
    print(modelOutput)

    print("---------------sentence output-------------")
    sentenceAnswer = getSentenceFromQuote(modelOutput['answer'], rawContent)
    print(sentenceAnswer)

    # print("---------------html output-----------------")
    # html = getHTMLOutput(topTopicLayer2, data)
    # f = open('html.html', 'w')
    # f.write(html)
    # f.close()
    # webbrowser.open_new_tab('file:///'+os.getcwd()+'/' + 'html.html')
    print("-------------------------------------------")