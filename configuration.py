# configuration.py

import configparser
import os
import sys

class Configuration():
    
    def __init__(self):
        
        self.config = configparser.ConfigParser()
        file = self.getDir()
        
        self.config.read(file)
        
    def getDir(self):
        path = os.path.realpath(__file__)      # Pfad ermitteln
        
        basename = self.checkPath(os.path.dirname(path))
        path = basename + '/crosscobra.ini'
        
        return path
        
    def getRun(self, system):
        return self.config['Run'][system]
    
    def getTerminal(self, system):
        return self.config['Terminal'][system]
    
    def getInterpreter(self, system):
        return self.config['Interpreter'][system]
    
    def getSystem(self):
        return self.config['System']['system']
    
    def getTab(self):
        return self.config['Tab']['tab']
    
    def getFont(self):
        return self.config['Font']['font']
    
    def setSystem(self, system):
        self.config['System']['system'] = system

        path = os.path.realpath(__file__)    
        basename = self.checkPath(os.path.dirname(path))

        iniPath = basename + "/crosscobra.ini"
        
        with open(iniPath, 'w') as f:
            self.config.write(f)

    def setStandard(self):
        config = configparser.ConfigParser()
        
        config['Run'] = {}
        config['Run']['mate'] = 'mate-terminal -x sh -c "python3 {}; exec bash"'
        config['Run']['gnome'] = 'gnome-terminal -- sh -c "python3 {}; exec bash"'
        config['Run']['kde'] = 'konsole --hold -e "python3 {}"'
        config['Run']['xterm'] = 'xterm -hold -e "python3 {}"'
        config['Run']['windows'] = 'start cmd /K python {}'
        config['Run']['mac'] = 'open -a Terminal ./python3 {}'
        
        config['Terminal'] = {}
        config['Terminal']['mate'] = 'mate-terminal'
        config['Terminal']['gnome'] = 'gnome-terminal'
        config['Terminal']['kde'] = 'konsole'
        config['Terminal']['xterm'] = 'xterm'
        config['Terminal']['windows'] = 'start cmd'
        config['Terminal']['mac'] = 'open -a Terminal ./' 
        
        config['Interpreter'] = {}
        config['Interpreter']['mate'] = 'mate-terminal -x "python3"'
        config['Interpreter']['gnome'] = 'gnome-terminal -- "python3"'
        config['Interpreter']['kde'] = 'konsole -e python3'
        config['Interpreter']['xterm'] = 'xterm python3'
        config['Interpreter']['windows'] = 'start cmd /K python'
        config['Interpreter']['mac'] = 'open -a Terminal ./python3'
        
        config['System'] = {}
        config['System']['system'] = ''
        
        config['Tab'] = {}
        config['Tab']['tab'] = '4'
        
        config['Font'] = {}
        config['Font']['font'] = '13'
        
        return config


    def checkPath(self, path):
        if '\\' in path:
            path = path.replace('\\', '/')
        return path

    
if __name__ == '__main__':
    c = Configuration()

    system = c.getSystem()
    runCommand = c.getRun(system)
    terminalCommand = c.getTerminal(system)
    interpreterCommand = c.getInterpreter(system)
    
    #c.setSystem('gnome')  
 
    print(system + ':\n' + runCommand + '\n' + terminalCommand + '\n' + interpreterCommand) 
    