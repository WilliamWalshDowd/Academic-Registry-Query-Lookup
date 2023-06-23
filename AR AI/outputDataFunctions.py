#----------------------------------------------Topic output lookup---------------------------------------------
def getOutput(title, dataVal, labels):
    for catagory, value in dataVal.items():
        for sheet in value:
            labels[catagory].append(sheet['Title'])
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

def makeTitleList(dataVal):
    justSheetLabels = []
    for catagory, value in dataVal.items():
        for sheet in value:
            justSheetLabels.append(sheet['Title'])
    return justSheetLabels

def getHTMLOutput(title, dataVal, labels):
    for catagory, value in dataVal.items():
        for sheet in value:
            labels[catagory].append(sheet['Title'])
            if sheet['Title'] == title:
                return sheet['html']
    return "No Matching Files In Data"

def compileSheetsToList(dataVal):
    justSheets = []
    for catagory, value in dataVal.items():
        for sheet in value:
            justSheets.append(sheet)
    return justSheets