import os
from PyQt5.QtWidgets import QAction

from PyQt5 import Qsci
from PyQt5.Qsci import QsciScintilla, QsciLexerPython, QsciAPIs
from PyQt5.QtGui import QFont, QFontMetrics, QColor
from PyQt5.Qt import Qt

import re

from runthread import RunThread
from configuration import Configuration


#######################################


class PythonLexer(QsciLexerPython):
    def __init__(self):
        super().__init__()
    
    def keywords(self, index):
        keywords = QsciLexerPython.keywords(self, index) or ''
        if index == 1:
            return 'self ' + ' super ' + keywords


######################################


class CodeEditor(QsciScintilla):

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.filename = None
        self.fileBrowser = None
        self.mainWindow = parent
        self.debugging = False
        
        c = Configuration()
        self.pointSize = int(c.getFont())
        self.tabWidth = int(c.getTab())
        
        # Scrollbars
        self.verticalScrollBar().setStyleSheet(
            """border: 20px solid black;
            background-color: darkgreen;
            alternate-background-color: #FFFFFF;""")
    
        self.horizontalScrollBar().setStyleSheet(
            """border: 20px solid black;
            background-color: darkgreen;
            alternate-background-color: #FFFFFF;""")
        
        # matched / unmatched brace color ...
        self.setMatchedBraceBackgroundColor(QColor('#000000'))
        self.setMatchedBraceForegroundColor(QColor('cyan'))
        self.setUnmatchedBraceBackgroundColor(QColor('#000000'))
        self.setUnmatchedBraceForegroundColor(QColor('red'))

        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        
        # edge mode ... line at 79 characters 
        self.setEdgeColumn(79)
        self.setEdgeMode(1)
        self.setEdgeColor(QColor('dark green'))

        # Set the default font
        self.font = QFont()
        self.font.setFamily('Mono')
        self.font.setFixedPitch(True)
        self.font.setPointSize(self.pointSize)
        self.setFont(self.font)
        self.setMarginsFont(self.font)

        # Margin 0 is used for line numbers
        fontmetrics = QFontMetrics(self.font)
        self.setMarginsFont(self.font)
        self.setMarginWidth(0, fontmetrics.width("00000") + 5)
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QColor("#000000"))
        self.setMarginsForegroundColor(QColor("#FFFFFF"))
        
        # Margin 1 for breakpoints
        self.setMarginType(1, QsciScintilla.SymbolMargin)
        self.setMarginWidth(1, "00")
        sym = QsciScintilla.Circle

        self.markerDefine(sym, 1)

        self.setMarginMarkerMask(0, 0b1111)
        
        handle_01 = self.markerAdd(1, 0) 

        # FoldingBox
        self.setFoldMarginColors(QColor('dark green'), QColor('dark green'))
        
        # CallTipBox
        self.setCallTipsForegroundColor(QColor('#FFFFFF'))
        self.setCallTipsBackgroundColor(QColor('#282828'))
        self.setCallTipsHighlightColor(QColor('#3b5784'))
        self.setCallTipsStyle(QsciScintilla.CallTipsContext)
        self.setCallTipsPosition(QsciScintilla.CallTipsBelowText)
        self.setCallTipsVisible(-1)
        
        # change caret's color
        self.SendScintilla(QsciScintilla.SCI_SETCARETFORE, QColor('#98fb98'))
        self.setCaretWidth(4)

        # tab Width
        self.setIndentationsUseTabs(False)
        self.setTabWidth(self.tabWidth)
        # use Whitespaces instead tabs
        self.SendScintilla(QsciScintilla.SCI_SETUSETABS, False)
        self.setAutoIndent(True)
        self.setTabIndents(True)

        # BackTab
        self.setBackspaceUnindents(True)

        # Current line visible with special background color or not :)
        #self.setCaretLineVisible(False)
        #self.setCaretLineVisible(True)
        #self.setCaretLineBackgroundColor(QColor("#020202"))               
        
        # not too small
        self.setMinimumSize(300, 300)
        
        # get style
        self.style = None
        
        # Call the Color-Function: ...
        self.setPythonStyle()
        
        #self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)

        # Contextmenu
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        undoAction = QAction("Undo", self)
        undoAction.triggered.connect(self.undoContext)
        redoAction = QAction("Redo", self)
        redoAction.triggered.connect(self.redoContext)
        sepAction1 = QAction("", self)
        sepAction1.setSeparator(True)
        cutAction = QAction("Cut", self)
        cutAction.triggered.connect(self.cutContext)
        copyAction = QAction("Copy", self)
        copyAction.triggered.connect(self.copyContext)
        pasteAction = QAction("Paste", self)
        pasteAction.triggered.connect(self.pasteContext)
        sepAction2 = QAction("", self)
        sepAction2.setSeparator(True)
        sepAction3 = QAction("", self)
        sepAction3.setSeparator(True)
        selectAllAction = QAction("Select All", self)
        selectAllAction.triggered.connect(self.getContext)
        terminalAction = QAction("Open Terminal", self)
        terminalAction.triggered.connect(self.termContext)
        
        self.addAction(undoAction)
        self.addAction(redoAction)
        self.addAction(sepAction1)
        self.addAction(cutAction)
        self.addAction(copyAction)
        self.addAction(pasteAction)
        self.addAction(sepAction2)
        self.addAction(selectAllAction)
        self.addAction(sepAction3)
        self.addAction(terminalAction)

        # signals
        self.SCN_FOCUSIN.connect(self.onFocusIn)
        self.textChanged.connect(self.onTextChanged)
        self.marginClicked.connect(self.onMarginClicked)

    def onFocusIn(self):
        self.mainWindow.refresh(self)

    def onTextChanged(self):
        notebook = self.mainWindow.notebook
        textPad = notebook.currentWidget()
        index = notebook.currentIndex()
        
        if self.debugging is True:
            self.mainWindow.statusBar.showMessage('remember to update CodeView if you delete or change lines in CodeEditor !', 3000)
        
        if textPad == None:
            return
        
        if textPad.filename:
            if not '*' in notebook.tabText(index):
                fname = os.path.basename(textPad.filename)
                fname += '*'
                notebook.setTabText(index, fname)
        
        else:
            fname = notebook.tabText(index)
            fname += '*'
            
            if not '*' in notebook.tabText(index):
                notebook.setTabText(index, fname)
        
    
    def onMarginClicked(self):
        pass
    

    def checkPath(self, path):
        if '\\' in path:
            path = path.replace('\\', '/')
        return path
    

    def undoContext(self):
        self.undo()
    
    def redoContext(self):
        self.redo()

    def cutContext(self):
        self.cut()
    
    def copyContext(self):
        self.copy()

    def pasteContext(self):
        self.paste()

    def getContext(self):
        self.selectAll()
    
    def termContext(self):
        c = Configuration()
        system = c.getSystem()
        command = c.getTerminal(system)
        
        thread = RunThread(command)
        thread.start()
 
    def getLexer(self):
        return self.lexer
    
    def setPythonStyle(self):
        self.style = 'Python'
        
        # Set Python lexer
        self.setAutoIndent(True)
        
        #self.lexer = QsciLexerPython()
        self.lexer = PythonLexer()
        self.lexer.setFont(self.font)
        self.lexer.setFoldComments(True)
        
        # set Lexer
        self.setLexer(self.lexer)
        
        self.setCaretLineBackgroundColor(QColor("#344c4c"))
        self.lexer.setDefaultPaper(QColor("black"))
        self.lexer.setDefaultColor(QColor("white"))
        self.lexer.setColor(QColor('white'), 0) # default
        self.lexer.setPaper(QColor('black'), -1) # default -1 vor all styles
        self.lexer.setColor(QColor('gray'), PythonLexer.Comment)  # = 1
        self.lexer.setColor(QColor('orange'), 2)   # Number = 2
        self.lexer.setColor(QColor('lightblue'), 3)   # DoubleQuotedString 
        self.lexer.setColor(QColor('lightblue'), 4)   # SingleQuotedString 
        self.lexer.setColor(QColor('#33cccc'), 5)   # Keyword 
        self.lexer.setColor(QColor('lightblue'), 6)   # TripleSingleQuotedString 
        self.lexer.setColor(QColor('lightblue'), 7)   # TripleDoubleQuotedString 
        self.lexer.setColor(QColor('#ffff00'), 8)   # ClassName 
        self.lexer.setColor(QColor('#ffff66'), 9)   # FunctionMethodName 
        self.lexer.setColor(QColor('magenta'), 10)   # Operator 
        self.lexer.setColor(QColor('white'), 11)   # Identifier 
        self.lexer.setColor(QColor('gray'), 12)   # CommentBlock 
        self.lexer.setColor(QColor('#ff471a'), 13)   # UnclosedString 
        self.lexer.setColor(QColor('gray'), 14)   # HighlightedIdentifier 
        self.lexer.setColor(QColor('#5DD3AF'), 15)   # Decorator 
        self.setPythonAutocomplete()
        self.setFold()


    def setPythonAutocomplete(self):
        
        self.autocomplete = QsciAPIs(self.lexer)
        self.keywords = self.lexer.keywords(1)
        
        self.keywords = self.keywords.split(' ')
        
        for word in self.keywords:
            self.autocomplete.add(word)
        
        self.autocomplete.add('super')
        self.autocomplete.add('self')
        self.autocomplete.add('__name__')
        self.autocomplete.add('__main__')
        self.autocomplete.add('__init__')
        self.autocomplete.add('__str__')
        self.autocomplete.add('__repr__')
        
        self.autocomplete.prepare()
        
        ## Set the length of the string before the editor tries to autocomplete
        self.setAutoCompletionThreshold(3)
        
        ## Tell the editor we are using a QsciAPI for the autocompletion
        self.setAutoCompletionSource(QsciScintilla.AcsAPIs)
        
        self.updateAutoComplete()
    

    def setFold(self):
        # setup Fold Styles for classes and functions ...
        x = self.FoldStyle(self.FoldStyle(5)) 
        #self.textPad.folding()
        if not x:
            self.foldAll(False)
        
        self.setFolding(x)
        #self.textPad.folding()  
        
    
    def unsetFold(self):
        self.setFolding(0)

    def keyReleaseEvent(self, e):
        # feed the autocomplete with the words from editor
        # simple algorithm to do this ... everytime after Enter

        # refresh CodeView
        text = self.text()
        self.updateCodeView(text)

        # if ENTER was hit ... :
        
        if e.key() == Qt.Key_Return:
        
            self.updateAutoComplete()
    
    def updateCodeView(self, text=''):
        codeView = self.mainWindow.codeView
        codeViewDict = codeView.makeDictForCodeView(text)
        codeView.updateCodeView(codeViewDict)
       
    
    def updateAutoComplete(self, text=None):

        if not text:
            
            firstList = []     # list to edit
            secondList = []    # collect all items for autocomplete
            
            text = self.text()

            # parse complete text ....
            firstList = text.splitlines()
            
            for line in firstList:
                if 'def' in line:
                    item = line.strip()
                    item = item.strip('def')
                    item = item.replace(':', '')
                    if not item in secondList:
                        secondList.append(item)
                elif 'class' in line:
                    item = line.strip()
                    item = item.strip('class')
                    item = item.replace(':', '')
                    if not item in secondList:
                        secondList.append(item)
            
            
            text = text.replace('"', " ").replace("'", " ").replace("(", " ").replace\
                                (")", " ").replace("[", " ").replace("]", " ").replace\
                                (':', " ").replace(',', " ").replace("<", " ").replace\
                                (">", " ").replace("/", " ").replace("=", " ").replace\
                                (";", " ")
                
            firstList = text.split('\n')
            
            for row in firstList:
                
                if (row.strip().startswith('#')) or (row.strip().startswith('//')):
                    continue
                
                else:
                    wordList = row.split() 
                    
                    for word in wordList:
                        
                        if re.match("(^[0-9])", word):
                            continue
                        
                        elif '#' in word or '//' in word:
                            continue
                        
                        elif word in self.keywords:
                            continue
                        
                        elif (word == '__init__') or (word == '__main__') or \
                             (word == '__name__') or (word == '__str__') or \
                             (word == '__repr__'):
                            continue
                        
                        elif word in secondList:
                            continue
                        
                        elif len(word) > 15:
                            continue
                        
                        elif not len(word) < 3:
                            w = re.sub("{}<>;,:]", '', word)
                            #print(w)
                            secondList.append(w)
            
            # delete doubled entries
            x = set(secondList)
            secondList = list(x)
            
            # debugging ...
            #print(secondList)

            for item in secondList:
                self.autocomplete.add(item)
            
            self.autocomplete.prepare()

    def setPythonPrintStyle(self):
        # Set None lexer
        self.font = QFont()
        self.font.setFamily('Mono')
        self.font.setFixedPitch(True)
        self.font.setPointSize(10)
        self.setFont(self.font)

        self.lexer = PythonLexer()
        self.lexer.setFont(self.font)
        # set Lexer
        self.setLexer(self.lexer)

        self.setCaretLineBackgroundColor(QColor("#344c4c"))
        self.lexer.setDefaultPaper(QColor("white"))
        self.lexer.setDefaultColor(QColor("black"))
        self.lexer.setColor(QColor('black'), -1) # default
        self.lexer.setPaper(QColor('white'), -1) # default
        self.lexer.setColor(QColor('gray'), PythonLexer.Comment)  # entspricht 1
        self.lexer.setColor(QColor('orange'), 2)   # Number entspricht 2
        self.lexer.setColor(QColor('darkgreen'), 3)   # DoubleQuotedString entspricht 3
        self.lexer.setColor(QColor('darkgreen'), 4)   # SingleQuotedString entspricht 4
        self.lexer.setColor(QColor('darkblue'), 5)   # Keyword entspricht 5
        self.lexer.setColor(QColor('darkgreen'), 6)   # TripleSingleQuotedString entspricht 6
        self.lexer.setColor(QColor('darkgreen'), 7)   # TripleDoubleQuotedString entspricht 7
        self.lexer.setColor(QColor('red'), 8)   # ClassName entspricht 8
        self.lexer.setColor(QColor('crimson'), 9)   # FunctionMethodName entspricht 9
        self.lexer.setColor(QColor('green'), 10)   # Operator entspricht 10
        self.lexer.setColor(QColor('black'), 11)   # Identifier entspricht 11 ### alle Wörter
        self.lexer.setColor(QColor('gray'), 12)   # CommentBlock entspricht 12
        self.lexer.setColor(QColor('#ff471a'), 13)   # UnclosedString entspricht 13
        self.lexer.setColor(QColor('gray'), 14)   # HighlightedIdentifier entspricht 14
        self.lexer.setColor(QColor('#5DD3AF'), 15)   # Decorator entspricht 15
    
        self.setNoneAutocomplete()
        self.unsetFold()
        
        self.font = QFont()
        self.font.setFamily('Mono')
        self.font.setFixedPitch(True)
        self.font.setPointSize(self.pointSize)



    def setNoneAutocomplete(self):
        #AutoCompletion
        self.autocomplete = Qsci.QsciAPIs(self.lexer)
        self.autocomplete.clear()

        self.autocomplete.prepare()

        self.setAutoCompletionThreshold(3)
        self.setAutoCompletionSource(QsciScintilla.AcsAPIs)
    

    def resetPythonPrintStyle(self, lexer):
        
        self.font = QFont()
        self.font.setFamily('Mono')
        self.font.setFixedPitch(True)
        self.font.setPointSize(self.pointSize)
        self.setFont(self.font)
        
        lexer.setFont(self.font)
        # set Lexer
        self.setLexer(lexer)
        
        # margins reset
        
        # Margin 0 is used for line numbers
        fontmetrics = QFontMetrics(self.font)
        self.setMarginsFont(self.font)
        self.setMarginWidth(0, fontmetrics.width("00000") + 5)
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QColor("#000000"))
        self.setMarginsForegroundColor(QColor("#FFFFFF"))

        # FoldingBox
        self.setFoldMarginColors(QColor('dark green'), QColor('dark green'))
    
