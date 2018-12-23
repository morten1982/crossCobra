import sys
import os

from PyQt5.QtWidgets import (QTabWidget, QMessageBox)

from codeeditor import CodeEditor
from widgets import MessageBox

class TabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__()
        
        self.mainWindow = parent
        self.setStyleSheet(
            '''
            background-color: #2c2c2c;
            color: white;
            alternate-background-color: #FFFFFF;
            selection-background-color: #3b5784;
            ''')
        self.setStyleSheet('''
            QTabBar::tab:selected {background: darkgreen;}
        ''')
        
        
        self.setMovable(True)
        self.setTabsClosable(True)
        
        # signals
        self.tabCloseRequested.connect(self.closeTab)
        self.currentChanged.connect(self.changeTab)
        
        self.textPad = None 
        self.codeView = None
    

    def newTab(self, editor=None, codeView=None):
        
        if not editor:
            editor = CodeEditor(parent=self.mainWindow)
            self.addTab(editor, "noname")
            editor.filename = None
           
            if self.mainWindow:
                self.codeView = self.mainWindow.codeView

            
        else:
            if editor.filename == None:
                self.addTab(editor, "noname")
            
            else:
                self.addTab(editor, os.path.basename(editor.filename))
                x = self.count() - 1
                self.setTabToolTip(x, editor.filename)
                self.codeView = self.mainWindow.codeView
        


    def closeTab(self, index):
        x = self.currentIndex()
        if x != index:
            self.setCurrentIndex(index)
        
        tabText = self.tabText(index)
        
        if '*' in tabText:
            q = MessageBox(QMessageBox.Warning, 'Warning',
                           'File not saved\n\nSave now ?',
                           QMessageBox.Yes | QMessageBox.No)
            if (q.exec_() == QMessageBox.Yes):
                self.mainWindow.save()
                self.removeTab(index)
            else:
                self.removeTab(index)
        else:
            self.removeTab(index)
        
        x = self.currentIndex()
        self.setCurrentIndex(x)
        
        if x == -1:
            self.refreshCodeView('')
            self.mainWindow.setWindowTitle('CrossCobra - Python IDE')
    
    
    def changeTab(self, index):
        x = self.count()
        y = x - 1
        
        if y >= 0:
            self.setCurrentIndex(index)
            textPad = self.currentWidget()
            self.textPad = textPad
            text = self.textPad.text()
            
            if self.codeView:
                self.refreshCodeView(text)
            else:
                self.codeView = self.mainWindow.codeView
                self.refreshCodeView(text)
        
        if self.textPad:
            self.mainWindow.refresh(self.textPad)
   
    def refreshCodeView(self, text=None):
        text = text
        codeViewDict = self.codeView.makeDictForCodeView(text)
        self.codeView.updateCodeView(codeViewDict)
    
    def getCurrentTextPad(self):
        textPad = self.currentWidget()
        return textPad
  