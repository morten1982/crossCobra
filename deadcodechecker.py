import io
import sys
import re

from vulture.core import Vulture
from contextlib import redirect_stdout


class DeadCodeChecker():
    
    def __init__(self, text):
        self.vultureObject = Vulture()
        self.vultureObject.scan(text)
        
    def getString(self):
        
        with io.StringIO() as buf, redirect_stdout(buf):

            self.vultureObject.report()
            output = buf.getvalue()


        newOutput = output.replace(':', '')
        return newOutput
    
    def getList(self):
        with io.StringIO() as buf, redirect_stdout(buf):

            self.vultureObject.report()
            output = buf.getvalue()


        newOutput = output.replace(':', '').split('\n')
        return newOutput
    
