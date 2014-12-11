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
        #self.rating = owner['regard'].duplicate()
        self.contacts = {'accepted' : 0, 'declined': 0, 'rejected': 0, 'total': 0}
            
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
        '''
        regard_range = self.owner['regard']['upper'] - self.owner['regard']['lower']
        relative_rating = (float(interaction.overall_rating/99) * regard_range) + self.owner['regard']['lower']
        self.rating.influence(relative_rating)

        self.rating.params['current'] = weightedAverage(self.rating.params['current'], self.entries, interaction.overall_rating, 1)
        
        
        self.broadcasts += interaction['total']['count']
        self.cycles_present += interaction.cycles_present
        
        for key in interaction.g_traits.keys():
            if key not in self.p_traits.keys():
                self.p_traits[key] = interaction.g_traits[key]
                
            else:
                self.p_traits[key] = weightedAverage(self.p_traits[key], self.entries, interaction.g_traits[key], 1)
                
        self.entries += 1
        '''
        
        self.broadcasts += interaction['total']['count']
        self.cycles_present += interaction.cycles_present
        
        for key in interaction.g_traits.keys():
            if key not in self.p_traits.keys():
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
        
        for key in self.p_traits.keys():
            trait_delta = abs(self.owner.getDesired(key) - self.p_traits[key])
            trait_rating = 99 - trait_delta
            rating_list.append(trait_rating)
            
        if len(rating_list) > 0:
            rating_coefficient = float(sum(rating_list) / len(rating_list))
            rating_coefficient /= 99
            
        else:
            rating_coefficient = self.owner['regard']['relative']
            
        if self.contacts['total'] > 0:
            rejected = self.contacts['rejected']
            accepted = self.contacts['accepted']
            declined = self.contacts['declined']
            total = self.contacts['total']
            
            contact_rating = (accepted + declined) / total
            rating_coefficient = (rating_coefficient + contact_rating) / 2.0
            
        regard_range = self.owner['regard']['upper'] - self.owner['regard']['lower']
        self.rating = (regard_range * rating_coefficient) + self.owner['regard']['lower']
        
        
    def addRejection(self):
        #print "\t\t%s rejects %s" % (self.perceived, self.owner)
        #print "\t\t\t%s perception of %s: %f" % (self.perceived, self.owner, self.perceived.getRating(self.owner))
        #print "\t\t\t%s perception of %s before: %f" % (self.owner, self.perceived, self.owner.getRating(self.perceived))
        self.contacts['rejected'] += 1
        self.contacts['total'] += 1
        self.updateRating()
        #print "\t\t\t%s perception of %s after: %f" % (self.owner, self.perceived, self.owner.getRating(self.perceived))
        
    def addAcceptance(self):
        #print "\t\t%s accepts %s" % (self.perceived, self.owner)
        #print "\t\t\t%s perception of %s: %f" % (self.perceived, self.owner, self.perceived.getRating(self.owner))
        #print "\t\t\t%s perception of %s before: %f" % (self.owner, self.perceived, self.owner.getRating(self.perceived))
        self.contacts['accepted'] += 1
        self.contacts['total'] += 1
        non_rejections = self.contacts['total'] - self.contacts['rejected']
        if non_rejections > 10:
            self.p_traits['sociable'] = self.contacts['accepted'] / float(non_rejections)
            self.p_traits['sociable'] *= 99
        self.updateRating()
        #print "\t\t\t%s perception of %s after: %f" % (self.owner, self.perceived, self.owner.getRating(self.perceived))
        
    def addUnavailable(self):
        #print "\t\t%s declines %s" % (self.perceived, self.owner)
        #print "\t\t\t%s perception of %s: %f" % (self.perceived, self.owner, self.perceived.getRating(self.owner))
        #print "\t\t\t%s perception of %s before: %f" % (self.owner, self.perceived, self.owner.getRating(self.perceived))
        #self.rating.influence(self.rating['base'])
        self.contacts['declined'] += 1
        self.contacts['total'] += 1
        if self.contacts['total'] > 10 and self.contacts['rejected'] != self.contacts['total']:
            self.p_traits['sociable'] = self.contacts['accepted'] / (self.contacts['accepted'] + self.contacts['declined'])
        self.updateRating()
        #print "\t\t\t%s perception of %s after: %f" % (self.owner, self.perceived, self.owner.getRating(self.perceived))
      
    '''      
    def guessValue(self, assumed_value):
        # adjust so regard makes perceived trait closer to desired, not increase or decrease
        regard_offset = (self.owner.p_traits['regard']['coefficient'] - .5) * 100
        adjusted_value = boundsCheck(assumed_value + regard_offset)
        return (assumed_value + adjusted_value) / 2 
    '''
            
    def printPerception(self):
        regard_range = self.owner['regard']['upper'] - self.owner['regard']['lower']
        delta_to_min = self.rating - self.owner['regard']['lower']
        relative_rating = delta_to_min / regard_range
        print "%s perception of %s: %f (%f relative)" % (self.owner, self.perceived, self.rating, relative_rating)
        #print "%s perception of %s: %f" % (self.perceived, self.owner, self.perceived.getRating(self.owner))
        print "(%d entries, %d cycles, %d broadcasts)" % (self.entries, self.cycles_present, self.broadcasts)
        for key in self.contacts.keys():
            print "\t%s: %d" % (key, self.contacts[key])
            
        for key in self.p_traits.keys():
            print "\t%s: %f" % (key, self.p_traits[key]), 
            print " (%f desired)" % self.owner.d_traits[key]['base'], 
            print " (%f actual)" % self.perceived.i_traits[key]['base']