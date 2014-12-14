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
        self.rating = owner.getCurrent('regard')
        self.contacts = {'accepted' : 0, 'declined': 0, 'rejected': 0, 'total': 0}
        # invitations from perceived to owner
        self.invitations = 0
        self.memories = 0
            
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
            
    def addInteraction(self, interaction, isMemory=False):
        
        if not isMemory:
            self.broadcasts += interaction['total']['count']
            self.cycles_present += interaction.cycles_present
            
        else:
            self.memories += 1
        
        for key in interaction.g_traits:
            if key not in self.p_traits:
                self.p_traits[key] = interaction.g_traits[key]
                
            else:
                self.p_traits[key] = weightedAverage(self.p_traits[key], self.entries, interaction.g_traits[key], 1)
                
        self.updateRating()
        
    # get % desirability from traits and contacts, calc rating relative to 
    # regard lower/upper bounds
    def updateRating(self):
        self.entries += 1
        rating_list = list()
        rating_coefficient = 0.0
        
        for key in self.p_traits:
            trait_delta = abs(self.owner.getDesired(key) - self.p_traits[key])
            trait_rating = 99 - trait_delta
            rating_list.append(trait_rating)
            
        if len(rating_list) > 0:
            rating_coefficient = float(sum(rating_list) / len(rating_list))
            rating_coefficient /= 99
            
        else:
            rating_coefficient = self.owner['regard']['relative']
            
        regard_range = self.owner['regard']['upper'] - self.owner['regard']['lower']
        self.rating = (regard_range * rating_coefficient) + self.owner['regard']['lower']
        
    def addRejection(self):
        self.contacts['rejected'] += 1
        self.contacts['total'] += 1
        self.updateRating()
        
    def addInvitation(self):
        self.invitations += 1
            
    def addAcceptance(self):
        self.contacts['accepted'] += 1
        self.contacts['total'] += 1
        non_rejections = self.contacts['total'] - self.contacts['rejected']
        if non_rejections > 10:
            self.p_traits['sociable'] = self.contacts['accepted'] / float(non_rejections)
            self.p_traits['sociable'] *= 99
        self.updateRating()
        
    def addUnavailable(self):
        self.contacts['declined'] += 1
        self.contacts['total'] += 1
        if self.contacts['total'] > 10 and self.contacts['rejected'] != self.contacts['total']:
            self.p_traits['sociable'] = self.contacts['accepted'] / (self.contacts['accepted'] + self.contacts['declined'])
        self.updateRating()
            
    def printPerception(self):
        regard_range = self.owner['regard']['upper'] - self.owner['regard']['lower']
        delta_to_min = self.rating - self.owner['regard']['lower']
        relative_rating = (delta_to_min / regard_range) * 99
        print "\t%s perception of %s: %f (%f relative)" % (self.owner, self.perceived, self.rating, relative_rating)
        print "\t(%d entries, %d cycles, %d broadcasts)" % (self.entries, self.cycles_present, self.broadcasts)
        print "\t%s has sent %d invitations to %s)" % (self.perceived, self.invitations, self.owner)
        print "\t%s has sent %d invitations to %s)" % (self.owner, self.contacts['total'], self.perceived)
        for contact in self.contacts:
            print "\t\t%s: %d" % (contact, self.contacts[contact])
            
        for trait in self.p_traits:
            print "\t\t%s: %f" % (key, self.p_traits[trait]), 
            print " (%f desired)" % self.owner.d_traits[trait]['base'], 
            print " (%f actual)" % self.perceived.i_traits[trait]['base'],
            print " (%d priority weight)" % self.owner.desire_priority[trait]