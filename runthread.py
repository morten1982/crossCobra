import os
import threading


class RunThread(threading.Thread):

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        os.system(self.command)
