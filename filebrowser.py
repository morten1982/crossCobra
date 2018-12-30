import os

from PyQt5.QtWidgets import (QTreeView, QFileSystemModel, QSizePolicy,
                             QAction, QMenu, QMessageBox)

from PyQt5.Qt import (QDir, QSizePolicy, QPalette, Qt, QFont)

from PyQt5.Qsci import QsciAPIs
from PyQt5 import Qsci

from PyQt5.Qt import Qt

from codeeditor import CodeEditor
from dialog import EnterDialog
from runthread import RunThread
from configuration import Configuration
from widgets import MessageBox

import shutil


class FileBrowser(QTreeView):
    def __init__(self, parent=None, textPad=None, notebook=None, 
                 codeView=None):
        super().__init__()
        self.path = self.checkPath(os.getcwd())
        self.filename = None
        
        self.text = None
        
        self.initItems()
        
        self.textPad = textPad
        self.notebook = notebook
        self.codeView = codeView
        
        self.mainWindow = parent
        
        self.index = None
        
        self.copySourceFilePath = None      # copy / paste items
        self.copySourceFileName = None
        self.isCopyFileFolder = None

        self.setStyleSheet(
            """
            border: 5 px;
            background-color: black; 
            color: white;
            alternate-background-color: #FFFFFF;
            selection-background-color: #3b5784;
            """)
        
        # Contextmenu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openMenu)
        
        self.popMenu = QMenu()
        self.popMenu.setStyleSheet(
        """
            color: #FFFFFF;
            background-color: #2c2c2c;
            selection-background-color: #3b5784;
            alternate-background-color: #FFFFFF;
        """
        )
        
        infoAction = QAction('Info', self)
        infoAction.triggered.connect(self.onInfo)
        createFolderAction = QAction('Create New Folder', self)
        createFolderAction.triggered.connect(self.onCreateNewFolder)
        copyAction = QAction('Copy Item', self)
        copyAction.triggered.connect(self.onCopy)
        pasteAction = QAction('Paste Item', self)
        pasteAction.triggered.connect(self.onPaste)
        renameAction = QAction('Rename Item', self)
        renameAction.triggered.connect(self.onRename)
        deleteAction = QAction('Delete Item', self)
        deleteAction.triggered.connect(self.onDelete)
        terminalAction = QAction('Open Terminal', self)
        terminalAction.triggered.connect(self.onTerminal)
        
        self.popMenu.addAction(infoAction)
        self.popMenu.addSeparator()
        self.popMenu.addAction(createFolderAction)
        self.popMenu.addSeparator()
        self.popMenu.addAction(copyAction)
        self.popMenu.addAction(pasteAction)
        self.popMenu.addAction(renameAction)
        self.popMenu.addSeparator()
        self.popMenu.addAction(deleteAction)
        self.popMenu.addSeparator()
        self.popMenu.addAction(terminalAction)
        
        
    def openMenu(self, position):
        # -> open ContextMenu 
        self.popMenu.exec_(self.mapToGlobal(position))

    def onInfo(self):
        if not self.index:
            return

        index = self.index
        indexItem = self.model.index(index.row(), 0, index.parent())
        
        fileName, filePath, fileDir, fileInfo = self.getFileInformation()

        bundle = fileInfo.isBundle()            # bool
        dir = fileInfo.isDir()                  # bool
        file = fileInfo.isFile()                # bool
        executable = fileInfo.isExecutable()    # bool
        readable = fileInfo.isReadable()        # bool
        writable = fileInfo.isWritable()        # bool
        created = fileInfo.created()            # QDateTime
        #modified = fileInfo.lastModified()      # QDateTime
        owner = fileInfo.owner()                # QString
        size = fileInfo.size()                  # QInt
        s = format(size, ',d')
        
        text = ''
        text += 'Type:\t'
        if bundle:
            text += 'Bundle\n\n'
        if dir:
            text += 'Path\n\n'
        if file:
            text += 'File\n\n'
        
        if readable:
            text += 'read:\tyes\n'
        else:
            text += 'read:\tno\n'
        if writable:
            text += 'write:\tyes\n'
        else:
            text += 'write:\tno\n'
        if executable:
            text += 'exec:\tyes\n\n'
        else:
            text += 'exec:\tno\n\n'
        
        text += 'size:\t' + str(s) + ' bytes' + '\n'
        text += 'owner:\t' + owner + '\n'
        text += 'created:\t' + str(created.date().day()) + '.' + \
                str(created.date().month()) + '.' + \
                str(created.date().year()) + '  ' + \
                created.time().toString() + '\n'

        q = MessageBox(QMessageBox.Information, fileName,          
                       text, QMessageBox.NoButton)
        q.exec_()



    
    def onCreateNewFolder(self):
        if not self.index:
            return
        else:
            index = self.index
            fileName, filePath, fileDir, fileInfo = self.getFileInformation()

            path = os.getcwd() + '/'
            path = self.checkPath(path)

        
        index = self.index
        fileName, filePath, fileDir, fileInfo = self.getFileInformation()

        dialog = EnterDialog(self.mainWindow, fileName, \
                             filePath, fileDir, fileInfo, False, path)
        dialog.exec_()
        
        # return
    
    def onCopy(self):
        if not self.index:
            return
        
        fileName, filePath, fileDir, fileInfo = self.getFileInformation()
        
        if fileName == '..':
            self.clearSelection()
            self.mainWindow.statusBar.showMessage("can't copy this item !", 3000)
            self.copySourceFilePath = None
            self.copySourceFileName = None
            self.isCopyFileFolder = None
            return
        
        if fileDir:
            self.copySourceFilePath = filePath
            self.copySourceFileName = fileName
            self.isCopyFileFolder = True
            self.mainWindow.statusBar.showMessage('Path: <' + \
                                                   self.copySourceFileName + \
                                                   '> marked', 3000)
        else:
            self.copySourceFilePath = filePath
            self.copySourceFileName = fileName
            self.mainWindow.statusBar.showMessage('File: <' + \
                                                   self.copySourceFileName + \
                                                   '> marked', 3000)
        
    def onPaste(self):
        if not self.index:
            return
        
        if not self.copySourceFilePath:
            self.mainWindow.statusBar.showMessage('nothing marked !', 3000)
            return
        
        if not self.copySourceFileName:
            self.mainWindow.statusBar.showMessage('nothing marked !', 3000)
            return

        
        fileName, filePath, fileDir, fileInfo = self.getFileInformation()
        
        rootPath = os.getcwd()
        rootPath = self.checkPath(rootPath)
        fileList = os.listdir(self.path)      # File list at current path

        if fileName == '..':
            # clicked on '..'
            rootPath = os.getcwd()
            rootPath = self.checkPath(rootPath)
        
        if fileDir and self.isCopyFileFolder:
            # copy path to another path
            if fileName == '..':
                path = os.getcwd()
                path = self.checkPath(path)
            else:
                path = filePath
            
            newPath = path + '/' + self.copySourceFileName
            fileList = os.listdir(path)
            
            if self.copySourceFileName in fileList:
                q = MessageBox(QMessageBox.Warning, "Error",
                      "Another path with the same name already exists.", 
                      QMessageBox.NoButton)
                q.exec_()
                
                self.resetMarkedItems(True)
                return
                
            if self.copySourceFilePath in newPath:

                q = MessageBox(QMessageBox.Critical, 'Error',
                      'Name of path already exists in new path',
                      QMessageBox.NoButton)
                
                q.exec_()
                self.resetMarkedItems(True)
                return
            
            try:
                os.mkdir(newPath)
                self.copytree(self.copySourceFilePath, newPath)
                self.mainWindow.statusBar.showMessage('Done !', 3000)
                
            except Exception as e:
                q = MessageBox(QMessageBox.Critical, "Error",
                    str(e), QMessageBox.NoButton)
                q.exec_()
                
                self.resetMarkedItems(True)
                return
            

        elif fileDir and not self.isCopyFileFolder:
            # copy file to path
            if fileName == '..':
                path = os.getcwd()
                path = self.checkPath(path)
            else:
                path = filePath
        
            fileList = os.listdir(path)      # File list at current path

            if self.copySourceFileName in fileList:
                result = MessageBox(QMessageBox.Warning, "Warning",
                         "File already exists.\n" +
                          "Continue ?", QMessageBox.Yes | QMessageBox.No)

                if (result.exec_() == QMessageBox.Yes):
                    
                    try:
                        shutil.copy(self.copySourceFilePath, path)
                        self.mainWindow.statusBar.showMessage('Done !', 3000)
                        
                    except Exception as e:
                        q = MessageBox(QMessageBox.Critical, "Error",
                            str(e), QMessageBox.NoButton)
                        q.exec_()
                        
                        self.resetMarkedItems(True)
                        return
                else:
                    self.resetMarkedItems()
                    return
            else:
                
                try:
                    shutil.copy(self.copySourceFilePath, path)
                    self.mainWindow.statusBar.showMessage('Done !', 3000)

                except Exception as e:
                    q = MessageBox(QMessageBox.Critical, "Error",
                        str(e), QMessageBox.NoButton)
                    q.exec_()
                    
                    self.resetMarkedItems(True)
                    return
        
        elif not fileDir and self.isCopyFileFolder:
            # copy path to selected file -> correct this user input ...
            newPath = rootPath + '/' + self.copySourceFileName

            if self.copySourceFileName in fileList:
                q = MessageBox(QMessageBox.Information, "Error",
                    "Another path with the same name already exists.", 
                    QMessageBox.NoButton)
                q.exec_()
                
                self.resetMarkedItems(True)
                return

            try:
                os.mkdir(newPath)
                self.copytree(self.copySourceFilePath, newPath)
                self.mainWindow.statusBar.showMessage('Done !', 3000)
                
            except Exception as e:
                q = MessageBox(QMessageBox.Critical, "Error",
                    str(e), QMessageBox.NoButton)
                q.exec_()
                
                self.resetMarkedItems(True)
                return

            
        elif not fileDir and not self.isCopyFileFolder:
            # user copy file to another file -> correct this input
            fileList = os.listdir(rootPath)      # File list in current path
            
            if self.copySourceFileName in fileList:
                result = MessageBox(QMessageBox.Warning, "Warning",
                         "File with this name already exists !" +
                          "Continue ?", QMessageBox.Yes | QMessageBox.No)

                
                if (result.exec_() == QMessageBox.Yes):
                    
                    try:
                        shutil.copy(self.copySourceFilePath, rootPath)
                        self.mainWindow.statusBar.showMessage('Done !', 3000)

                    except Exception as e:
                        q = MessageBox(QMessageBox.Critical, "Error",
                            str(e), QMessageBox.NoButton)
                        q.exec_()
                        
                        self.resetMarkedItems(True)                    
                    return
                
                else:
                    self.resetMarkedItems(True)
                    return
            
            else:
                
                try:
                    shutil.copy(self.copySourceFilePath, rootPath)
                    self.mainWindow.statusBar.showMessage('Done !', 3000)

                except Exception as e:
                    q = MessageBox(QMessageBox.Critical, "Error",
                        str(e), QMessageBox.Ok)
                    q.exec_()
                    
                    self.resetMarkedItems(True)
                    return
                    
        self.resetMarkedItems()
    
    def resetMarkedItems(self, showMessage=False):
        # reset marked items
        self.copySourceFilePath = None
        self.copySourceFileName = None
        self.isCopyFileFolder = None
        
        if showMessage:
            self.mainWindow.statusBar.showMessage('Mark removed !', 3000)

    # copy path with subfolder
    #  thanks to stackoverflow.com ..... ! 
    def copytree(self, src, dst, symlinks=False, ignore=None):
        if not os.path.exists(dst):
            os.makedirs(dst)
        if not os.path.exists(src):
            os.makedirs(src)
            
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            
            if os.path.isdir(s):
                self.copytree(s, d, symlinks, ignore)
            else:
                if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                    shutil.copy2(s, d)

    
    def onRename(self):
        if not self.index:
            return
        
        fileName, filePath, fileDir, fileInfo = self.getFileInformation()

        dialog = EnterDialog(self.mainWindow, fileName, filePath, fileDir, fileInfo, True)
        dialog.exec_()

    
    def onDelete(self):
        if not self.index:
            return

        fileName, filePath, fileDir, fileInfo = self.getFileInformation()

        if fileDir:
            if fileName == '..':
                self.mainWindow.statusBar.showMessage('can not delete this item !', 3000)
                return
            else:
                result = MessageBox(QMessageBox.Warning, 'Delete directory', '<b>' + filePath + '</b>' + "  ?", 
                         QMessageBox.Yes | QMessageBox.No)

                if (result.exec_() == QMessageBox.Yes):
                    try:
                        shutil.rmtree(filePath)
                        self.mainWindow.statusBar.showMessage('Done !', 3000)
                        self.resetMarkedItems()
                        
                    except Exception as e:
                        q = MessageBox(QMessageBox.Critical, "Error", str(e), QMessageBox.NoButton)
                        q.exec_()
                        
                        self.resetMarkedItems(True)
                else:
                    return        

        else:
            pathList = filePath.split('/')[:-1]
            path = ''
            for elem in pathList:
                path += elem + '/'
            file = filePath.split('/')[-1]
            result = MessageBox(QMessageBox.Warning, 'Delete file', path + "<b>" + file + "</b>" + "  ?", 
                                 QMessageBox.Yes | QMessageBox.No)

            if (result.exec_() == QMessageBox.Yes):
                try:
                    os.remove(filePath)
                    self.mainWindow.statusBar.showMessage('Done !', 3000)
                except Exception as e:
                    q = MessageBox(QMessageBox.Critical, "Error", str(e), QMessageBox.NoButton)

                    q.exec_()
                    
                    self.resetMarkedItems(True)


    
    def onTerminal(self):
        c = Configuration()
        system = c.getSystem()
        command = c.getTerminal(system)
        
        thread = RunThread(command)
        thread.start()

    
    def initItems(self):
        font = QFont()
        font.setPixelSize(16)
        
        self.prepareModel(os.getcwd())

        self.setToolTip(os.getcwd())
        
        # prepare drag and drop
        self.setDragEnabled(False)

        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.setSizePolicy(sizePolicy)
        self.setAutoExpandDelay(2)
        self.setAlternatingRowColors(False)
        self.setAnimated(False)
        self.setIndentation(20)
        self.setSortingEnabled(False)
        self.setRootIsDecorated(False)
        self.setPalette(QPalette(Qt.black))
        
        self.verticalScrollBar().setStyleSheet(
           """border: 20px solid black;
            background-color: darkgreen;
            alternate-background-color: #FFFFFF;""")

        self.horizontalScrollBar().setStyleSheet(
           """border: 20px solid black;
            background-color: darkgreen;
            alternate-background-color: #FFFFFF;""")


        self.setFont(font)
        
        # signals
        self.doubleClicked.connect(self.onDoubleClicked)
        self.clicked.connect(self.onClicked)
        self.pressed.connect(self.onClicked)
        #self.entered.connect(self.onEntered)
        self.columnMoved()
        
        # that hides the size, file type and last modified colomns
        self.setHeaderHidden(True)
        self.hideColumn(1)
        self.hideColumn(2)
        self.hideColumn(3)
        self.resize(400, 400)

    def prepareModel(self, path):
        self.model = QFileSystemModel()
        self.model.setRootPath(path)
        #model.setFilter(QDir.AllDirs |QDir.NoDotAndDotDot | QDir.AllEntries)
        self.model.setFilter(QDir.Files | QDir.AllDirs | QDir.NoDot | QDir.Hidden)  
        #self.model.setNameFilters(self.filter)
        
        self.model.rootPathChanged.connect(self.onRootPathChanged)
                
        self.fsindex = self.model.setRootPath(path)
        
        self.setModel(self.model)
        self.setRootIndex(self.fsindex)


    def checkPath(self, path):
        if '\\' in path:
            path = path.replace('\\', '/')
        return path


    def getFileInformation(self):
        index = self.index
        indexItem = self.model.index(index.row(), 0, index.parent())

        fileName = self.model.fileName(indexItem)
        filePath = self.model.filePath(indexItem)
        fileDir = self.model.isDir(indexItem)
        fileInfo = self.model.fileInfo(indexItem)
            
        fileName = self.checkPath(fileName)
        filePath = self.checkPath(filePath)
        
        return(fileName, filePath, fileDir, fileInfo)



    def onClicked(self, index):
        self.index = index       #.... index des FileSystemModels
        indexItem = self.model.index(index.row(), 0, index.parent())
        
        fileName, filePath, fileDir, fileInfo = self.getFileInformation()
        self.setToolTip(filePath)
        
        if fileDir:
            self.path = self.checkPath(os.getcwd())
            self.filename = None
        else:
            self.filename = filePath
            self.path = self.checkPath(os.getcwd())
        
        #print('self.filename: ', self.filename)
        #print('self.path: ', self.path)


    def refresh(self, dir=None):
        if not dir:
            dir = self.checkPath(os.getcwd())
        else:
            dir = dir
        
        self.model.setRootPath(dir)
        
        if self.rootIsDecorated:
            self.setRootIsDecorated(False)
        
        self.clearSelection()

    
    def onDoubleClicked(self, index):
        self.index = index      #.... wie oben ... def onClicked(...):
        indexItem = self.model.index(index.row(), 0, index.parent())
        
        fileName, filePath, fileDir, fileInfo = self.getFileInformation()

        if fileDir:
            filePath = self.checkPath(filePath)
            try:
                os.chdir(filePath)
            except Exception as e:
                self.mainWindow.statusBar.showMessage(str(e), 3000)
            self.path = self.checkPath(os.getcwd())
            
            self.model.setRootPath(filePath)
            
            if self.rootIsDecorated:
                self.setRootIsDecorated(False)
            
        else:
            self.filename = filePath
            
            try:
                with open(self.filename, 'r') as f:
                    self.text = f.read()
            except Exception as e:
                self.mainWindow.statusBar.showMessage(str(e), 3000)
                
                self.filename = None
                return
            
            # debug
            if self.textPad:
            
                if not self.textPad.filename:
                    editor = CodeEditor(self.mainWindow)
                    editor.setText(self.text) 
                    editor.filename = filePath
                    self.notebook.newTab(editor)
                    self.textPad = editor
                    
                    x = self.notebook.count()   # number of tabs
                    index = x - 1
                    self.notebook.setCurrentIndex(index)
                    tabName = os.path.basename(editor.filename)
                    
                    self.notebook.setTabText(x, tabName)
                    self.textPad = editor
                    #self.textPad.filename = filePath
                    
                else:
                    editor = CodeEditor(self.mainWindow)
                    editor.setText(self.text)
                    editor.filename = filePath
                    tabName = os.path.basename(editor.filename)
                    self.notebook.newTab(editor)
                    x = self.notebook.count()   # number of tabs
                    index = x - 1
                    self.notebook.setCurrentIndex(index)
                    self.textPad = editor
                    #self.textPad.filename = filePath
           
            if not self.textPad:
                    editor = CodeEditor(self.mainWindow)
                    editor.filename = None
                    self.notebook.newTab(editor)
                    x = self.notebook.count()
                    index = x - 1
                    self.notebook.setCurrentIndex(index)
                    self.textPad = editor
                    #self.textPad.filename = filePath
           
            # make codeView
            codeViewList = self.codeView.makeDictForCodeView(self.text)
            self.codeView.updateCodeView(codeViewList)
            
            # update textPad Autocomplete
            autocomplete = Qsci.QsciAPIs(self.textPad.lexer)
            self.textPad.autocomplete = autocomplete
            self.textPad.setPythonAutocomplete()
            
        self.clearSelection()
        self.textPad.updateAutoComplete()
   
    def onRootPathChanged(self):
        self.setModel(None)
        self.setModel(self.model)
        self.fsindex = self.model.setRootPath(QDir.currentPath())
        self.setRootIndex(self.fsindex)
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.setSizePolicy(sizePolicy)
        self.setAutoExpandDelay(2)
        self.setAlternatingRowColors(False)
        self.setAnimated(True)
        self.setIndentation(20)
        self.setSortingEnabled(False)
        self.setRootIsDecorated(False)
        
        self.setHeaderHidden(True)
        self.hideColumn(1)
        self.hideColumn(2)
        self.hideColumn(3)
        self.setToolTip(QDir.currentPath())
        self.path = os.getcwd()
        self.path = self.checkPath(self.path)
