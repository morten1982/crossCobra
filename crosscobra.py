#!/usr/local/bin/python3

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget,
                             QHBoxLayout,
                             QToolBar,QAction, QSplitter,
                             QFileDialog, QStatusBar, QDialog,
                             QSizePolicy, QPushButton,
                             QLineEdit, QDesktopWidget, QShortcut)
from PyQt5.QtGui import QIcon
from PyQt5.Qt import Qt
from PyQt5.QtPrintSupport import QPrintDialog
from PyQt5.Qsci import QsciPrinter
from PyQt5 import QtCore

from pathlib import Path

from codeeditor import CodeEditor
from filebrowser import FileBrowser
from tabwidget import TabWidget
from codeview import CodeView
from runthread import RunThread
from configuration import Configuration
from dialog import SettingsDialog, EnterDialog, HelpDialog


class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.setStyleSheet(
            """
                color: white;
                background-color: #2c2c2c;
                selection-background-color: #3b5784
            """)

        
        path = os.path.abspath(__file__)
        self.HOME = os.path.dirname(path) + '/'
        self.setWindowIcon(QIcon(self.HOME + 'images/crosscobra.png'))

        # change to Home Path
        os.chdir(Path.home())

        self.fileBrowser = None
        
        self.initUI()
        self.centerOnScreen()
        
        helpAction = QAction(self)
        helpAction.setShortcut('F1')
        helpAction.triggered.connect(self.help)
        
        self.addAction(helpAction)
    
    def initUI(self):        
        self.setGeometry(300, 300, 1200, 600)
        self.setWindowTitle('CrossCobra - Python IDE')
        
        # splitters
        splitter1 = QSplitter(Qt.Vertical)
        splitter2 = QSplitter(Qt.Horizontal)
        
        # widgets
        self.notebook = TabWidget(self)
        self.codeView = CodeView(self, self.notebook)

        self.notebook.newTab(codeView=self.codeView)

        self.textPad = self.notebook.textPad

        self.fileBrowser = FileBrowser(self, self.textPad, self.notebook, self.codeView)
        self.textPad.fileBrowser = self.fileBrowser

        # add widgets to splitters
        splitter1.addWidget(self.fileBrowser)
        splitter1.addWidget(self.codeView)
        w = splitter1.width()
        splitter1.setSizes([w/2, w/2])
        
        splitter2.addWidget(splitter1)
        splitter2.addWidget(self.notebook)
        
        hbox = QHBoxLayout()
        hbox.addWidget(splitter2)
        
        splitter1.setStretchFactor(1, 1)
        splitter2.setStretchFactor(1, 10)
        
        self.setCentralWidget(splitter2)
        
        # actions
        newAction = QAction(QIcon(self.HOME + 'images/new.png'), 'New', self)    

        newAction.setShortcut('Ctrl+N')
        newAction.triggered.connect(self.new)
        
        openAction = QAction(QIcon(self.HOME + 'images/open.png'), 'Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.triggered.connect(self.open)
        
        saveAction = QAction(QIcon(self.HOME + 'images/save.png'), 'Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.triggered.connect(self.save)
        
        saveAsAction = QAction(QIcon(self.HOME + 'images/saveAs.png'), 'Save As', self)
        saveAsAction.setShortcut('Ctrl+Shift+S')
        saveAsAction.triggered.connect(self.saveAs)
        
        printAction = QAction(QIcon(self.HOME + 'images/print.png'), 'Print', self)
        printAction.setShortcut('Ctrl+P')
        printAction.triggered.connect(self.onPrint)
        
        undoAction = QAction(QIcon(self.HOME + 'images/undo.png'), 'Undo', self)
        undoAction.setShortcut('Ctrl+Z')
        undoAction.triggered.connect(self.undo)

        redoAction = QAction(QIcon(self.HOME + 'images/redo.png'), 'Redo', self)
        redoAction.setShortcut('Ctrl+Shift+Z')
        redoAction.triggered.connect(self.redo)
        
        zoomInAction = QAction(QIcon(self.HOME + 'images/zoomIn.png'), 'ZoomIn', self)
        zoomInAction.setShortcut('Ctrl++')
        zoomInAction.triggered.connect(self.zoomIn)

        zoomOutAction = QAction(QIcon(self.HOME + 'images/zoomOut.png'), 'ZoomOut', self)
        zoomOutAction.setShortcut('Ctrl+-')
        zoomOutAction.triggered.connect(self.zoomOut)
        
        settingsAction = QAction(QIcon(self.HOME + 'images/settings.png'), 'Settings', self)
        settingsAction.setShortcut('F9')
        settingsAction.triggered.connect(self.showSettings)
              
        interpreterAction = QAction(QIcon(self.HOME + 'images/interpreter.png'), 'Start Python Interpreter', self)
        interpreterAction.setShortcut('F10')
        interpreterAction.triggered.connect(self.interpreter)
        
        terminalAction = QAction(QIcon(self.HOME + 'images/terminal.png'), 'Start Terminal', self)
        terminalAction.setShortcut('F11')
        terminalAction.triggered.connect(self.terminal)

        runAction = QAction(QIcon(self.HOME + 'images/run.png'), 'Run File', self)
        runAction.setShortcut('F12')
        runAction.triggered.connect(self.run)
        
        searchShortcut = QShortcut(self)
        searchShortcut.setKey('Ctrl+F')
        searchShortcut.activated.connect(self.onSearch)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # make toolbar
        self.toolbar = QToolBar()
        self.toolbar.setStyleSheet('''
            QToolButton::hover { background-color: darkgreen;}
        ''')

        self.toolbar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(Qt.RightToolBarArea, self.toolbar)
        
        self.toolbar.addSeparator()        
        self.toolbar.addAction(newAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(openAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(saveAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(saveAsAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(printAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(undoAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(redoAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(zoomInAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(zoomOutAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(settingsAction)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(spacer)
        self.toolbar.addAction(interpreterAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(terminalAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(runAction)

      
        # make statusbar
        self.statusBar = QStatusBar()
        self.searchEdit = QLineEdit()
        spacer2 = QWidget()

        self.searchEdit.setStyleSheet(
            '''
                background-color: white;
                color: black;
            ''')
        self.searchEdit.returnPressed.connect(self.onSearch)
        self.searchButton = QPushButton(QIcon(self.HOME + 'images/search.png'), 'Search', self)
        self.searchButton.setStyleSheet(
        '''
            QPushButton::hover { background-color: darkgreen;}
        ''')
        self.searchButton.clicked.connect(self.onSearch)
        self.statusBar.addPermanentWidget(spacer2)
        self.statusBar.addPermanentWidget(self.searchEdit)
        self.statusBar.addPermanentWidget(self.searchButton)
        self.setStatusBar(self.statusBar)
        # show all
        self.textPad.setFocus()
        self.show()
        
    def new(self):
        editor = CodeEditor(parent=self)
        editor.filename = None
        
        self.notebook.newTab(editor)
        
        x = self.notebook.count()
        index = x - 1
        
        self.notebook.setCurrentIndex(index)
        self.textPad = editor
        self.notebook.textPad = editor
        self.mainWindow = self.textPad.mainWindow

    def open(self):
        dialog = QFileDialog(self)
        dialog.setViewMode(QFileDialog.List)
        dialog.setDirectory(os.getcwd())

        filename = dialog.getOpenFileName(self, "Save")
        
        if filename[0]:
            filePath = filename[0]
            
            try:
                with open(filePath, 'r') as f:
                    text = f.read()
                
                editor = CodeEditor(self)
                editor.setText(text) 
                editor.filename = filePath
                
                self.notebook.newTab(editor)
                x = self.notebook.count()   # number of tabs
                index = x - 1
                self.notebook.setCurrentIndex(index)
                
                tabName = os.path.basename(editor.filename)    
                self.notebook.setTabText(x, tabName)
                self.textPad = editor    
            
            except Exception as e:
                self.statusBar.showMessage(str(e), 3000)
            

    def save(self):
        filename = self.textPad.filename
        index = self.notebook.currentIndex()
        tabText = self.notebook.tabText(index)
        
        if not filename:
            self.saveAs()
        
        else:
            text = self.textPad.text()
            try:
                with open(filename, 'w') as file:
                    file.write(text)
                    self.statusBar.showMessage(filename + " saved", 3000)
                    
                    # remove '*' in tabText
                    fname = os.path.basename(filename)
                    self.notebook.setTabText(index, fname)
                    
            except Exception as e:
                self.statusBar.showMessage(str(e), 3000)
                self.saveAs()
    
    
    def saveAs(self):
        ## to do ....
        dialog = QFileDialog(self)
        dialog.setViewMode(QFileDialog.List)
        dialog.setDirectory(os.getcwd())

        filename = dialog.getSaveFileName(self, "Save")
        
        if filename[0]:
            fullpath = filename[0]
            text = self.textPad.text()
            try:
                with open(fullpath, 'w') as file:
                    file.write(text)
                    self.statusBar.showMessage(fullpath + " saved", 3000)
                                    
                    # update all widgets
                    
                    self.textPad.filename = fullpath
                    self.refresh(self.textPad)
                    self.fileBrowser.refresh()
                    fname = os.path.basename(fullpath)
                    index = self.notebook.currentIndex()
                    self.notebook.setTabText(index, fname)

            except Exception as e:
                self.statusBar.showMessage(str(e), 3000)
        
        else:
            self.statusBar.showMessage('File not saved !', 3000)
    
    
    def onPrint(self):
        doc = QsciPrinter()
        dialog = QPrintDialog(doc, self)
        dialog.setWindowTitle('Print')

        if (dialog.exec_() == QDialog.Accepted):
            self.textPad.setPythonPrintStyle()
            try:
                doc.printRange(self.textPad)
            except Exception as e:
                print(str(e))
                
        else:
            return
        
        self.textPad.setPythonStyle()

    def undo(self):
        self.textPad.undo()

    def redo(self):
        self.textPad.redo()
    
    def zoomIn(self):
        self.textPad.zoomIn()
    
    def zoomOut(self):
        self.textPad.zoomOut()

    def showSettings(self):
        dialog = SettingsDialog(self, self.textPad)
        dialog.setModal(False)
        dialog.exec_()
    
    def interpreter(self):
        c = Configuration()
        system = c.getSystem()
        command = c.getInterpreter(system)
        
        thread = RunThread(command)
        thread.start()
    
    def terminal(self):
        c = Configuration()
        system = c.getSystem()
        command = c.getTerminal(system)
        
        thread = RunThread(command)
        thread.start()
    
    def run(self):
        self.save()
        c = Configuration()
        system = c.getSystem()
        command = c.getRun(system).format(self.textPad.filename)
        
        if not self.textPad.filename:
            self.statusBar.showMessage("can't run without filename !", 3000)
            return 
            
        thread = RunThread(command)
        thread.start()
    
    def onSearch(self):
        text = self.searchEdit.text()
        if text is '':
            self.statusBar.showMessage("can't start search without word", 3000) 
            return
        else:
            x = self.textPad.findFirst(text, False, True, False, True, True) # case sensitive
    
            if x == False:
                l = len(self.searchEdit.text())
                self.searchEdit.setSelection(0, l)
                self.searchEdit.setFocus()
                self.statusBar.showMessage('<' + text + '> not found', 3000)

    def refresh(self, textPad=None):
        if not textPad:
            return
                 
        self.textPad = textPad

        if not self.textPad.filename:
            self.setWindowTitle('CrossCobra - Python IDE')
            return
        
        dir = os.path.dirname(self.textPad.filename)
        
        try:
            os.chdir(dir)
            self.setWindowTitle(self.textPad.filename)
        
        except Exception as e:
            self.statusBar.showMessage(str(e), 3000)
            
        self.fileBrowser.refresh(dir)
        self.codeView.refresh()
    
    def centerOnScreen(self):
        res = QDesktopWidget().screenGeometry()
        self.move((res.width() / 2) - (self.frameSize().width() / 2),
                  (res.height() / 2) - (self.frameSize().height() / 2))

    def help(self):
        helpdialog = HelpDialog(self)
        helpdialog.exec_()
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    sys.exit(app.exec_())