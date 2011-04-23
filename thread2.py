# -*- coding: utf-8 -*-
import threading

class Thread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check 
    regularly for the stopped() condition.""" 
    def __init__(self, type, funct, main): 
        super(Thread, self).__init__() 
        self._stop = threading.Event() # BUG
        self.funct = funct
        self.type = type
        self.val = {}
        self.main = main
    def stop(self):
        if 'im_self' in dir(self.funct) and 'stop' in dir(self.funct.im_self):
            self.funct.im_self.stop()
        self._stop.set() # BUG
    def stopped(self): 
        return self._stop.isSet()
    def run(self):
        self.val.update(self.funct())
        self.main.callBack(self.type, self.val)

class Threads(threading.Thread):
    def __init__(self, threads, callback, main): 
        super(Threads, self).__init__()
        self._stop = threading.Event()
        self.threads = threads
        self.callback = callback
        self.main = main
    def stop(self):
        self._stop.set()
    def stopped(self):
        return self._stop.isSet()
    def run(self):
        for thread in self.threads:
            thread.join()
        self.callback()
        #self.val = self.funct()
        #self.main.callBack(self.type, self.val)