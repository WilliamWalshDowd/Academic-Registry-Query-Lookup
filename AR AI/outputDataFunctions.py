#-------------------------------------------Data & Output lookup---------------------------------------------
def getOutput(title, dataVal, labels):
    for catagory, value in dataVal.items():
        for sheet in value:
            labels[catagory].append(sheet['Title'])
            if sheet['Title'] == title:
                return sheet['Content']
    return "No Matching Files In Data"
        
def getSentenceFromQuote(quote, text):
    sentences = []
    for sentence in text.split(". "):
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
            justSheets.append({'Title' : sheet['Title'], 'Content' : sheet['Content']})
    return justSheets

def compileSheetContentToList(dataVal):
    fullSheet = ""
    for catagory, value in dataVal.items():
        for sheet in value:
            fullSheet += (sheet['Title'] + "\n" + sheet['Content'] + ".\n\n")
    return fullSheet

def findLabelFromQuote(quote, dataVal):
    for catagory, value in dataVal.items():
        for sheet in value:
            if quote in sheet['Content']:
                return sheet['Title']
    return "NO SHEET FOUND"

def getAmountOfLabels(dataVal):
    count = 0
    for catagory, value in dataVal.items():
        for sheet in value:
            count += 1
    return count

def printDataTitle(dataVal):
    for catagory, value in dataVal.items():
        print('\n' + catagory)
        for sheet in value:
            print("   " + sheet['Title'])

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()