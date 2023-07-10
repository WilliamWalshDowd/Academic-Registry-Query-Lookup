import json
import timeit
from outputDataFunctions import *
from transformers import pipeline

#---------------load course data---------------------
file = open('courseData.json', encoding="utf8")
courseData = json.load(file)

#---------------Model Loader-------------------------
model_name = "deepset/bert-large-uncased-whole-word-masking-squad2"
nlp = pipeline('question-answering', model=model_name, tokenizer=model_name)

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
    output = classifier(input, labels, multi_label=True)
    formatedOutput = []
    for i in range(len(labels)):
        formatedOutput.append(output['labels'][i] + ': ' + str(round(output['scores'][i]*100, 3)) + "%")
    return formatedOutput

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
        print("----------------Topics---------------------")
        #layer 1
        topics = get_topics(query, courseDataNames(courseData))
        for values in topics:
            print(values)
        #layer 1 best result key
        topTopicLayer1 = (str(topics[0]).split(":"))[0]

        print("---------------Label output layer 1--------")
        # print(str(topics[0]))
        # rawContent = getOutput(topTopicLayer1, data, LABELS)
        # print(rawContent)

        print("---------------Course output-------------")
        for i in courseData:
            if i['Name'] == topTopicLayer1:
                print(i)
                
        stop = timeit.default_timer()
        print("\n" + "Time taken: " + str(round((stop-start), 1)) + " seconds")
        print("-------------------------------------------")