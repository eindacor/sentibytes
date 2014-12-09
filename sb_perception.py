#from sb_communication import session, transmission, interaction
from sb_utilities import getCoefficient, calcInfluence, calcAccuracy, boundsCheck, weightedAverage, valueState

class perception(object):
    def __init__(self, perceived, owner):
        self.perceived = perceived
        self.owner = owner
        self.p_traits = {}
        self.entries = 0
        self.broadcasts = 0
        self.cycles_present = 0
        self.rating = owner['regard'].duplicate()
        
        # assume other's traits and states are same as owner's, adjust for regard
        for key in owner.d_traits.keys():
            assumed_value = owner.i_traits[key]['current']
            self.p_traits[key] = self.guessValue(assumed_value)
            
    def __getitem__(self, index):
        return self.p_traits[index]
    
    def __eq__(self, other):
        return self.rating == other.rating
        
    def __ne__(self, other):
        return self.rating != other.rating
    
    def __lt__(self, other):
        return self.rating < other.rating
        
    def __le__(self, other):
        return self.rating <= other.rating
        
    def __gt__(self, other):
        return self.rating > other.rating
        
    def __ge__(self, other):
        return self.rating >= other.rating
            
    def addInteraction(self, interaction):
        print "\t\t%s interacts with %s" % (self.perceived, self.owner)
        print "\t\t\t%s perception of %s before: %f" % (self.owner, self.perceived, self.owner.getRating(self.perceived))
        print "\t\t\tinteraction rating: %f" % interaction.rating
        self.rating.influence(interaction.rating)
        self.broadcasts += interaction['total']['count']
        self.cycles_present += interaction.cycles_present
        print "\t\t\t%s perception of %s after: %f" % (self.owner, self.perceived, self.owner.getRating(self.perceived))
        self.entries += 1
        
    def addRejection(self):
        print "\t\t%s rejects %s" % (self.perceived, self.owner)
        print "\t\t\t%s perception of %s: %f" % (self.perceived, self.owner, self.perceived.getRating(self.owner))
        print "\t\t\t%s perception of %s before: %f" % (self.owner, self.perceived, self.owner.getRating(self.perceived))
        self.rating.influence(self.rating['lower'])
        print "\t\t\t%s perception of %s after: %f" % (self.owner, self.perceived, self.owner.getRating(self.perceived))
        
    def addAcceptance(self):
        print "\t\t%s accepts %s" % (self.perceived, self.owner)
        print "\t\t\t%s perception of %s: %f" % (self.perceived, self.owner, self.perceived.getRating(self.owner))
        print "\t\t\t%s perception of %s before: %f" % (self.owner, self.perceived, self.owner.getRating(self.perceived))
        self.rating.influence(self.rating['upper'])
        print "\t\t\t%s perception of %s after: %f" % (self.owner, self.perceived, self.owner.getRating(self.perceived))
        
    def addUnavailable(self):
        print "\t\t%s declines %s" % (self.perceived, self.owner)
        #print "\t\t\t%s perception of %s: %f" % (self.perceived, self.owner, self.perceived.getRating(self.owner))
        #print "\t\t\t%s perception of %s before: %f" % (self.owner, self.perceived, self.owner.getRating(self.perceived))
        #self.rating.influence(self.rating['base'])
        #print "\t\t\t%s perception of %s after: %f" % (self.owner, self.perceived, self.owner.getRating(self.perceived))
            
    def guessValue(self, assumed_value):
        # adjust so regard makes perceived trait closer to desired, not increase or decrease
        regard_offset = (self.owner.p_traits['regard']['coefficient'] - .5) * 100
        adjusted_value = boundsCheck(assumed_value + regard_offset)
        return (assumed_value + adjusted_value) / 2 
            
    def printPerception(self):
        print "%s perception of %s: %f" % (self.owner, self.perceived, self.owner.getRating(self.perceived))
        print "%s perception of %s: %f" % (self.perceived, self.owner, self.perceived.getRating(self.owner))
        print "(%d entries, %d cycles, %d broadcasts)" % (self.entries, self.cycles_present, self.broadcasts)
        
        for key in self.p_traits.keys():
            print "\t%s: %f" % (key, self.p_traits[key]), 
            print " (%f desired)" % self.owner.d_traits[key]['base'], 
            print " (%f actual)" % self.perceived.i_traits[key]['base']
            
    def getCurrent(self):
        return self.rating['current']