import sys
import os
import json
from transformers import pipeline

#---------------load course data---------------------
file = open('../DataFiles/courseData.json', encoding="utf8")
courseData = json.load(file)

#----------------------------------------------------
def courseDataNames(data):
    list = []
    for i in data:
        list.append(i['Name'])
    return list

if __name__ == "__main__":
    print("----COURSES----")
    courseNames = courseDataNames(courseData)
    print(courseNames)
    while True:
        print("what course are you looking for?")
        query = input('>')
        for i in courseNames:
            if query in i:
                print(i)