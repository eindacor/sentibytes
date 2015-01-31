from random import random

class temporaryState(object):
    def __init__(self, duration, traits_effected, contagious=0):
        self.cycles_remaining = duration
        self.traits_effected = traits_effected
        self.contagious = contagious
        
    def procContagious(self):
        return random() < self.contagious