import sys
import os

from PyQt5.QtWidgets import (QApplication, QWidget, QDialog, QHBoxLayout,
                             QVBoxLayout, QGridLayout, QLabel, QLineEdit,
                             QPushButton, QMainWindow, QRadioButton,
                             QGroupBox, QSpinBox, 
                             QDialogButtonBox, QMessageBox, QListWidget,
                             QListWidgetItem, QFontDialog)
from PyQt5.QtGui import (QFont, QColor, QPalette)
from PyQt5.Qt import Qt
from configuration import Configuration

from widgets import (MessageBox, Label, RadioButton, PushButton, 
                     ListWidget, WhiteLabel, TabWidget, TextEdit)
from deadcodechecker import DeadCodeChecker
from pycodechecker import PyCodeChecker

class Dialog(QDialog):

    def __init__(self, parent=None, textPad=None):
        super().__init__()
        palette = QPalette()
        role = QPalette.Background
        palette.setColor(role, QColor('#2c2c2c'))
        self.setGeometry(parent.x() + 200 , parent.y() + 100, 500, 400)
        self.setPalette(palette)
        self.mainWindow = parent


class SettingsDialog(Dialog):

    def __init__(self, parent=None, textPad=None):
        super().__init__(parent, textPad)
        self.parent = parent
        self.textPad = textPad
        self.setWindowTitle('Settings')
        self.initUI()
    
    def initUI(self):
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        grid = QGridLayout()
        
        runLabel = Label('Run Command: ')

        terminalLabel = Label('Terminal Command: ')
        interpreterLabel = Label('Interpreter Command: ')

        self.c = Configuration()
        system = self.c.getSystem()
        
        runCommand = self.c.getRun(system)
        terminalCommand = self.c.getTerminal(system)
        interpreterCommand = self.c.getInterpreter(system)
        
        self.runBox = QLineEdit(runCommand)
        self.runBox.setCursorPosition(0)
        self.runBox.setMinimumWidth(30)
        self.terminalBox = QLineEdit(terminalCommand)
        self.terminalBox.setCursorPosition(0)
        self.interpreterBox = QLineEdit(interpreterCommand)
        self.interpreterBox.setCursorPosition(0)
        
        okButton = PushButton('OK')
        okButton.pressed.connect(self.close)
        
        groupBox1 = self.createRadioGroup()
        groupBox2 = self.createTextPadGroup()
        
        self.checkRadio(system)
              
        grid.addWidget(runLabel, 0, 0)
        grid.addWidget(self.runBox, 0, 1)
        grid.addWidget(terminalLabel, 1, 0)
        grid.addWidget(self.terminalBox, 1, 1)
        grid.addWidget(interpreterLabel, 2, 0)
        grid.addWidget(self.interpreterBox, 2, 1)
        grid.addWidget(okButton, 4, 1)
        grid.addWidget(groupBox1, 3, 0)
        grid.addWidget(groupBox2, 3, 1)
        
        self.setLayout(grid)
        
        self.show()
    
    def createRadioGroup(self):
        groupBox = QGroupBox('Commands')
        
        self.radio1 = RadioButton('Gnome')
        self.radio1.toggled.connect(lambda:self.radioState(self.radio1))
                
        self.radio2 = RadioButton('Mate')
        self.radio2.toggled.connect(lambda:self.radioState(self.radio2))

        self.radio3 = RadioButton('KDE')
        self.radio3.toggled.connect(lambda:self.radioState(self.radio3))

        self.radio4 = RadioButton('xterm')
        self.radio4.toggled.connect(lambda:self.radioState(self.radio4))

        self.radio5 = RadioButton('Windows')
        self.radio5.toggled.connect(lambda:self.radioState(self.radio5))

        self.radio6 = RadioButton('Mac OS')
        self.radio6.toggled.connect(lambda:self.radioState(self.radio6))

        vbox = QVBoxLayout()
        vbox.addWidget(self.radio1)
        vbox.addWidget(self.radio2)
        vbox.addWidget(self.radio3)
        vbox.addWidget(self.radio4)
        vbox.addWidget(self.radio5)
        vbox.addWidget(self.radio6)
        
        groupBox.setLayout(vbox)
        
        return groupBox
    
    def createTextPadGroup(self):
        groupBox = QGroupBox('Codeeditor')
                # tabWidthBox
        
        label1 = Label('Width for <Tab> in whitespaces:')

        self.tabWidthBox = QSpinBox()
        self.tabWidthBox.setMinimum(2)
        self.tabWidthBox.setMaximum(10)
        tab = int(self.c.getTab())
        self.tabWidthBox.setValue(tab)

        label2 = Label('Font size:')

        self.fontSizeBox = QSpinBox()
        self.fontSizeBox.setMinimum(6)
        self.fontSizeBox.setMaximum(30)
        fontSize = int(self.c.getFontSize())
        self.fontSizeBox.setValue(fontSize)
        
        label3 = WhiteLabel('Changes in this area will be appear on\nrestart or new Tab')
        vbox = QVBoxLayout()
        
        vbox.addWidget(label1)
        vbox.addWidget(self.tabWidthBox)
        vbox.addWidget(label2)
        vbox.addWidget(self.fontSizeBox)

        vbox.addWidget(label3)
        
        groupBox.setLayout(vbox)
        
        return groupBox
        
    def checkRadio(self, system):
        if system == 'gnome':
            self.radio1.setChecked(1)
        elif system == 'mate':
            self.radio2.setChecked(1)
        elif system == 'kde':
            self.radio3.setChecked(1)
        elif system == 'xterm':
            self.radio4.setChecked(1)
        elif system == 'windows':
            self.radio5.setChecked(1)
        elif system == 'mac':
            self.radio6.setChecked(1)
    
    def radioState(self, b):
        c = Configuration()
        if b.text() == 'Gnome':
            if b.isChecked() == True:
                c.setSystem('gnome')
                system = c.getSystem()
                
                runCommand, terminalCommand, interpreterCommand = self.getCommands(c, system)
                
                self.changeLineEdit(runCommand, terminalCommand, interpreterCommand)
        
        if b.text() == 'Mate':
            if b.isChecked() == True:
                c.setSystem('mate')
                system = c.getSystem()

                runCommand, terminalCommand, interpreterCommand = self.getCommands(c, system)

                self.changeLineEdit(runCommand, terminalCommand, interpreterCommand)
                
                
        if b.text() == 'KDE':
            if b.isChecked() == True:
                c.setSystem('kde')
                system = c.getSystem()

                runCommand, terminalCommand, interpreterCommand = self.getCommands(c, system)

                self.changeLineEdit(runCommand, terminalCommand, interpreterCommand)

        if b.text() == 'xterm':
            if b.isChecked() == True:
                c.setSystem('xterm')
                system = c.getSystem()

                runCommand, terminalCommand, interpreterCommand = self.getCommands(c, system)

                self.changeLineEdit(runCommand, terminalCommand, interpreterCommand)

        if b.text() == 'Windows':
            if b.isChecked() == True:
                c.setSystem('windows')
                system = c.getSystem()

                runCommand, terminalCommand, interpreterCommand = self.getCommands(c, system)

                self.changeLineEdit(runCommand, terminalCommand, interpreterCommand)

        if b.text() == 'Mac OS':
            if b.isChecked() == True:
                c.setSystem('mac')
                system = c.getSystem()

                runCommand, terminalCommand, interpreterCommand = self.getCommands(c, system)

                self.changeLineEdit(runCommand, terminalCommand, interpreterCommand)


    def changeLineEdit(self, runCommand, terminalCommand, interpreterCommand):
        self.runBox.clear()
        self.runBox.setText(runCommand)
        self.runBox.setCursorPosition(0)
        self.terminalBox.clear()
        self.terminalBox.setText(terminalCommand)
        self.terminalBox.setCursorPosition(0)
        self.interpreterBox.clear()
        self.interpreterBox.setText(interpreterCommand)
        self.interpreterBox.setCursorPosition(0)
    
    def getCommands(self, c, system):
        runCommand = c.getRun(system)
        terminalCommand = c.getTerminal(system)
        interpreterCommand = c.getInterpreter(system)
        
        return runCommand, terminalCommand, interpreterCommand
    

    def close(self):
        if self.radio1.isChecked():
            system = 'gnome'
        elif self.radio2.isChecked():
            system = 'mate'
        elif self.radio3.isChecked():
            system = 'kde'
        elif self.radio4.isChecked():
            system = 'xterm'
        elif self.radio5.isChecked():
            system = 'windows'
        elif self.radio6.isChecked():
            system = 'mac'
             
        runCommand = self.runBox.text()
        interpreterCommand = self.interpreterBox.text()
        terminalCommand = self.terminalBox.text()
        
        tab = self.tabWidthBox.value()
        fontSize = self.fontSizeBox.value()

        value = system
        config = self.c.setStandard()
        
        if value == 'mate':
            config['System']['system'] = 'mate'
            config['Run']['mate'] = runCommand
            config['Terminal']['mate'] = terminalCommand
            config['Interpreter']['mate'] = interpreterCommand
            config['Tab']['tab'] = str(tab)
            config['Size']['size'] = str(fontSize)
    
        elif value == 'gnome':
            config['System']['system'] = 'gnome'
            config['Run']['gnome'] = runCommand
            config['Terminal']['gnome'] = terminalCommand
            config['Interpreter']['gnome'] = interpreterCommand
            config['Tab']['tab'] = str(tab)
            config['Size']['size'] = str(fontSize)


        elif value == 'kde':
            config['System']['system'] = 'kde'
            config['Run']['kde'] = runCommand
            config['Terminal']['kde'] = terminalCommand
            config['Interpreter']['kde'] = interpreterCommand
            config['Tab']['tab'] = str(tab)
            config['Size']['size'] = str(fontSize)


        elif value == 'xterm':
            config['System']['system'] = 'xterm'
            config['Run']['xterm'] = runCommand
            config['Terminal']['xterm'] = terminalCommand
            config['Interpreter']['xterm'] = interpreterCommand
            config['Tab']['tab'] = str(tab)
            config['Size']['size'] = str(fontSize)


        elif value == 'windows':
            config['System']['system'] = 'windows'
            config['Run']['windows'] = runCommand
            config['Terminal']['windows'] = terminalCommand
            config['Interpreter']['windows'] = interpreterCommand
            config['Tab']['tab'] = str(tab)
            config['Size']['size'] = str(fontSize)


        elif value == 'mac':
            config['System']['system'] = 'mac'
            config['Run']['mac'] = runCommand
            config['Terminal']['mac'] = terminalCommand
            config['Interpreter']['mac'] = interpreterCommand
            config['Tab']['tab'] = str(tab)
            config['Size']['size'] = str(fontSize)

        else:
            return
        
        thisFile = os.path.realpath(__file__)     
        base = os.path.dirname(thisFile)
        base = self.checkPath(base)
    
        iniPath = base + "/crosscobra.ini"
        with open(iniPath, 'w') as f:
            config.write(f)
        

        self.destroy()



    def checkPath(self, path):
        if '\\' in path:
            path = path.replace('\\', '/')
        return path


class EnterDialog(QDialog):
    def __init__(self, parent, fileName, filePath, fileDir, fileInfo, rename=True, folderPath=None):
        super().__init__(parent)
        
        self.fileName = fileName
        self.filePath = filePath
        self.fileDir = fileDir
        self.fileInfo = fileInfo
        self.rename = rename
        self.folderPath = folderPath
        
        self.initUI()
        
    def initUI(self):
        self.setModal(True)
        
        if self.rename == True:
            if self.fileDir:
                self.setWindowTitle('Rename Directory')
            else:
                self.setWindowTitle('Rename File')
        
        elif self.rename == False:
            self.setWindowTitle('Create Directory')
        
        layout = QVBoxLayout()
        
        if self.rename == True:
            self.label = QLabel(self.fileName)
            
        elif self.rename == False:
            self.label = QLabel('in: ' + self.folderPath)
        
        self.text = QLineEdit()
        self.text.setPlaceholderText("Enter name")
        
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        
        layout.addWidget(self.label)
        layout.addWidget(self.text)
        layout.addWidget(self.buttonBox)
        
        self.setLayout(layout)
        
        if self.rename == True:
            self.buttonBox.accepted.connect(self.accept)
        elif self.rename == False:
            self.buttonBox.accepted.connect(self.acceptMakeFolder)
        
        # for both dialogs (rename / make)
        self.buttonBox.rejected.connect(self.onReject)
        
        self.fileName = self.checkPath(self.fileName)
        self.filePath = self.checkPath(self.filePath)
        

    def checkPath(self, path):
        if '\\' in path:
            path = path.replace('\\', '/')
        return path

    def accept(self):
        if self.fileDir:

            if self.label.text() == '..':
                self.close()
    
            newName = self.text.text()
            cutPaths = self.filePath.split('/')[:-1]
            path = '/'.join(cutPaths)
            newPathName = path +  '/' + newName
            if self.text.text() == '':
                return
            try:
                os.rename(self.filePath, newPathName)
            except Exception as e:
                q = MessageBox(QMessageBox.Critical, 'Error', 'Could not rename path\n\n' + str(e),
                                QMessageBox.NoButton)
                q.exec_()
            
        if not self.fileDir:
            newName = self.text.text()
            oldFileName = self.filePath.split('/')[-1]
            path = self.filePath.split(oldFileName)[0]
            newFilename = path + newName
            
            # check if file exists
            for file in os.listdir(path):
                if file == newName:
                    result = MessageBox(QMessageBox.Question, 'Warning', 'File already exists\n' +
                                                 'Continue ?', QMessageBox.Yes | QMessageBox.No)

                    if (result.exec_() == QMessageBox.No):
                        return
            
            try:
                os.rename(self.filePath, newFilename)
            except Exception as e:
                q = MessageBox(QMessageBox.Critical, 'Error', 'Could not rename file\n\n' + str(e),
                                QMessageBox.NoButton)

                q.exec_()
           
        self.close() 
    
    def acceptMakeFolder(self):
        sourcePath = self.folderPath
        newPath = self.text.text()
        if newPath.startswith('/'):
            newPath = newPath.strip('/')
        fullNewPath = sourcePath + newPath
        try:
            os.mkdir(fullNewPath)
        except Exception as e:
            q = MessageBox(QMessageBox.Critical, 'Error', 'Could not make directory\n\n' + str(e),
                                QMessageBox.NoButton)

            q.exec_()
        
        self.close()

    def onReject(self):
        self.close()


class FindDeadCodeDialog(QDialog):
    
    def __init__(self, parent, textPad, codeView):
        super().__init__()

        self.mainWindow = parent
        self.textPad = textPad
        self.codeView = codeView
        
        palette = QPalette()
        role = QPalette.Background
        palette.setColor(role, QColor('#2c2c2c'))
        self.setGeometry(self.codeView.x()+ 200, self.codeView.y(), 400, 300)
        self.setPalette(palette)

        self.setWindowTitle('Find Dead Code (using vulture)')
        self.initUI()

    
    def initUI(self):
        filename = os.path.basename(self.textPad.filename)
        vbox = QVBoxLayout()
        
        self.label = WhiteLabel(filename + ' :\n\n')
        self.label.setAlignment(Qt.AlignCenter)

        self.listWidget = ListWidget()

        updateButton = PushButton('Save + Update')
        updateButton.clicked.connect(self.update)
        okButton = PushButton('Ok')
        okButton.clicked.connect(self.onClose)
        
        hbox = QHBoxLayout()
        hbox.addWidget(updateButton)
        hbox.addWidget(okButton)

        
        vbox.addWidget(self.label)
        vbox.addWidget(self.listWidget)
        vbox.addLayout(hbox)
        
        self.setLayout(vbox)
        
        self.fillList()
        
        # signals
        self.listWidget.itemDoubleClicked.connect(self.gotoPos)
        
        self.show()

    def update(self):
        self.listWidget.clear()
        self.mainWindow.save()
        self.fillList()
    
    def fillList(self):
        filename = os.path.basename(self.textPad.filename)
        self.label.setText(filename)
        
        text = self.textPad.text()
        deadCodeChecker = DeadCodeChecker(text)
        outputList = deadCodeChecker.getList()
        
        self.lineNumberList = []
        self.codeList = []
        
        for elem in outputList:
            textList = elem.split(' ')
            self.lineNumberList.append(textList[0])
            codeText = ''
            
            for elem in textList[1:]:
                codeText += ' ' + elem
            
            self.codeList.append(codeText)
       
        i = 0
        for elem in self.codeList[0:-1]:
            item = QListWidgetItem()
            text = 'Line: ' + str(self.lineNumberList[i]) + '\t-> ' + str(self.codeList[i])
            pos = int(self.lineNumberList[i])
            item.setText(text)
            self.listWidget.addItem(item)
            i += 1
    
    def gotoPos(self):
        row = self.listWidget.currentRow()
        linenumber = int(self.lineNumberList[row])-1
        
        if linenumber >= 0:
            
            lineText = self.textPad.text(linenumber)
            rawcode = self.codeList[row]
            code = rawcode[rawcode.find("'")+1:rawcode.rfind("'")]
            
            x = self.textPad.findFirst(code, False, True, False, True, True,
                                       line=linenumber, index=0)
            
            self.listWidget.clearSelection()
            self.textPad.setFocus()

        
    def onClose(self):
        self.destroy()


class PyCodeCheckerDialog(QDialog):
    
    def __init__(self, parent, textPad, codeView):
        super().__init__()

        self.mainWindow = parent
        self.textPad = textPad
        self.codeView = codeView
        
        palette = QPalette()
        role = QPalette.Background
        palette.setColor(role, QColor('#2c2c2c'))
        self.setGeometry(self.codeView.x()+ 200, self.codeView.y(), 400, 300)
        self.setPalette(palette)

        self.setWindowTitle('Make Codestyle Check (using pyspellchecker)')
        self.initUI()

    
    def initUI(self):
        filename = os.path.basename(self.textPad.filename)
        vbox = QVBoxLayout()
        
        self.label = WhiteLabel(filename + ' :\n\n')
        self.label.setAlignment(Qt.AlignCenter)

        self.listWidget = ListWidget()
        
        updateButton = PushButton('Save + Update')
        updateButton.clicked.connect(self.update)
        okButton = PushButton('Ok')
        okButton.clicked.connect(self.onClose)
        
        hbox = QHBoxLayout()
        hbox.addWidget(updateButton)
        hbox.addWidget(okButton)
        
        vbox.addWidget(self.label)
        vbox.addWidget(self.listWidget)
        vbox.addLayout(hbox)
        
        self.setLayout(vbox)
        
        self.fillList()
        
        # signals
        self.listWidget.itemDoubleClicked.connect(self.gotoPos)
        
        self.show()

    def update(self):
        self.listWidget.clear()
        self.mainWindow.save()
        self.fillList()

    def fillList(self):
        filename = os.path.basename(self.textPad.filename)
        self.label.setText(filename)
        
        check = PyCodeChecker(filename)
        text = check.getString()
        self.lineList, self.cursorList, self.textList = check.getListFromString(text)

        i = 0
        for elem in self.textList:
            item = QListWidgetItem()
            try:
                text = 'Line: ' + str(self.lineList[i]) + '  Pos: ' + str(self.cursorList[i]) + \
                        '  ' + str(self.textList[i])
                item.setText(text)
                self.listWidget.addItem(item)

            except Exception as e:
                item.destroy()

            i += 1
    
    def gotoPos(self):
        row = self.listWidget.currentRow()
        
        line = self.lineList[row]
        cursor = self.cursorList[row]
        
        self.textPad.setSelection(int(line)-1, int(cursor)-1, int(line)-1, int(cursor))

        
    def onClose(self):
        self.destroy()
        


class HelpDialog(QDialog):
    
    def __init__(self, parent):
        super().__init__()

        self.mainWindow = parent
        self.setStyleSheet(
            """
                color: white;
                background-color: #2c2c2c;
                selection-background-color: #3b5784
            """)

        self.setGeometry(self.mainWindow.x()+ 200, self.mainWindow.y(), 600, 600)

        self.setWindowTitle('Help')
        self.initUI()

    
    def initUI(self):
        self.tabs = TabWidget()
        
        tab1 = TextEdit()
        tab1.setReadOnly(True)
        tab2 = TextEdit()
        tab2.setReadOnly(True)
        tab3 = TextEdit()
        tab3.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)

        self.tabs.addTab(tab1, "Shortcuts")
        self.tabs.addTab(tab2, "Codeeditor")
        self.tabs.addTab(tab3, "About")
        
        self.setLayout(layout)
        
#################################
        ##
        # Tab Shortcut Help
        ##
  
        shortcut_text = '''
        Shortcuts:
        
        New File\t-\tCtrl + N
        Open File\t-\tCtrl + O
        Save File\t-\tCtrl + S
        Save As\t\t-\tCtrl + Shift + S
        Print\t\t-\tCtrl + P
        Quit\t\t-\tAlt + F4
        Undo\t\t-\tCtrl + Z
        Redo\t\t-\tCtrl + Shift + Z
        Copy\t\t-\tCtrl + C
        Cut\t\t-\tCtrl + X
        Paste\t\t-\tCtrl + V
        Select All\t-\tCtrl + A

        Autocomplete\t-\tTab
        Search\t\t-\tCtrl + F

        Settings\t-\tF9
        Interpreter\t-\tF10
        Terminal\t-\tF11
        Run File\t-\tF12
        Zoom In\t-\tCtrl + +
        Zoom Out\t-\tCtrl + -

        Show Help\t-\tF1
        
        '''
        tab1.setText(shortcut_text)

        ##
        # Tab Codeeditor Help
        ##
        
        codeeditor_text = '''
        CrossCobra - The cross platform Python IDE
        
        CrossCobra is an Editor and Integrated Development Environment (IDE)
        for the "Python Programming Language".
        
        It shows the "python source code" colored (syntax highlighting) and 
        helps you to code with its own auto-complete function.
        
        It can run the codefile (requirement is, that you have installed 
        Python on your OS)
        It can also run the "Python Interpreter" and a terminal window 
        (specific for your current OS) -> this can be modified in the 
        settings (-> which where saved in crosscobra.ini => it's a text file)
        
        On the bottom-right, you find a search button with which you can 
        search the current file for a specific word.
        
        On the left side it has its own file-explorer to 
        copy, delete, rename ... files and folders. Use the pop-up menu
        (right mousebutton).
        
        The Codeview Window on the left bottom side shows you all classes 
        and functions for the current opened file.
        
        You can use the right mousebutton to find dead code (using vulture) 
        or to check if your code is styled correctly (using pycodestyle)
        
        To use these two functions you should have installed vulture 
        and pycodestyle.
        Use "pip3 install vulture" and "pip3 install pycodestyle" to
        install these packages
        
        Crosscobra is using 
        
        PyQt5\t\t5.11.3
        QScintilla\t2.10.8
        vulture\t\t1.0
        pycodestyle\t2.4.0
        '''
        
        tab2.setText(codeeditor_text)
        
        ##
        # Tab About Help
        ##

        about_text = '''
        CrossCobra 1.0
        
        
        Programmed 2018 by morbidMo
        
        
        I's open source software. You can modify and use the sourcecode -
        make it better or fork it on github.com:
        
        
        https://github.com/morten1982/crosscobra
        
        
        no guarantee of using it - it's your own risk :)
        
        
        CrossCobra was completely coded in Python using
        PyQt5, QScintilla, pycodestyle, vulture
        
        
        '''

        tab3.setText(about_text)
##################################
        
        self.show()

    def onClose(self):
        self.destroy()


class Main(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        dialog = SettingsDialog(self)
        dialog.exec_()
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Main()
    sys.exit(app.exec_())
