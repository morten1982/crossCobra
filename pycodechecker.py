import io
from pycodestyle import Checker
from contextlib import redirect_stdout


class PyCodeChecker():

    def __init__(self, filename):
        self.checker = Checker(filename)
    
    def getString(self):
        
        with io.StringIO() as buf, redirect_stdout(buf):

            self.checker.check_all()
            output = buf.getvalue()

        return output
    
    def getListFromString(self, text):
        
        rawList = []

        rawList = text.split("\n")
        
        parseList = []
        for line in rawList:
            obj = line.split(':')
            parseList.append(obj)

        lineList = []
        cursorList = []
        textList = []
        
        for obj in parseList[:-1]:  # last element is ''
            lineList.append(obj[1])
            cursorList.append(obj[2])
            textList.append(obj[3])

        return lineList, cursorList, textList
