from PyQt5.QtWidgets import (QMessageBox, QLabel, QRadioButton,
                             QPushButton, QListWidget, QTabWidget,
                             QTextEdit)


class MessageBox(QMessageBox):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet(
            '''
                color: white;
                background-color: #2c2c2c;
            ''')


class Label(QLabel):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet(
            '''
                color: darkgreen;
            ''')


class WhiteLabel(QLabel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet(
            '''
                color: white;
            ''')


class PushButton(QPushButton):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet(
            '''
                color: #FFFFFF;
                background-color: #2c2c2c;
            ''')


class RadioButton(QRadioButton):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet(
            '''
                color: darkgreen;
            ''')


class ListWidget(QListWidget):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet(
            '''
                color: white;
                background-color: #000000;
            ''')
        
        self.verticalScrollBar().setStyleSheet(
           """border: 20px solid black;
            background-color: darkgreen;
            alternate-background-color: #FFFFFF;""")

        self.horizontalScrollBar().setStyleSheet(
           """border: 20px solid black;
            background-color: darkgreen;
            alternate-background-color: #FFFFFF;""")


class TabWidget(QTabWidget):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
            

class TextEdit(QTextEdit):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet(
            '''
                color: #FFFFFF;
                background-color: #2c2c2c;
            ''')
            
        self.verticalScrollBar().setStyleSheet(
           """border: 20px solid black;
            background-color: darkgreen;
            alternate-background-color: #FFFFFF;""")

        self.horizontalScrollBar().setStyleSheet(
           """border: 20px solid black;
            background-color: darkgreen;
            alternate-background-color: #FFFFFF;""")