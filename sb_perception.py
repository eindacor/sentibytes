from sb_utilities import getCoefficient, calcInfluence, calcAccuracy, \
    boundsCheck, combineAverages, valueState, listAverage, averageContainer

class perception(object):
    def __init__(self, other_ID, owner):
        self.other_ID = other_ID
        self.owner_ID = owner.sentibyte_ID
        self.perceived_traits = {}
        self.interaction_count = 0
        self.broadcasts_observed = 0
        self.cycles_observed = 0
        self.rumors_heard = 0
        self.memories_counted = 0
        self.rating = 0
        # trust level will eventually override proc('trusting') in communication
        self.trust = 0.0
        
        # regard coefficient must be inverted. higher regard means assumed value
        # will be closer to what the owner desires
        inverted_regard_coefficient = 1 - owner['regard']['coefficient']
        for trait in owner.d_traits:
            desired_value = owner.getDesired(trait)
            assumed_value = calcAccuracy(desired_value, inverted_regard_coefficient, max_offset=20)
            self.perceived_traits[trait] = assumed_value
            
        self.updateRating(owner)
            
    def __getitem__(self, index):
        return self.perceived_traits[index]
    
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
            
    def addInteraction(self, interaction, owner, isMemory=False, isRumor=False):
        if isRumor:
            self.rumors_heard += 1
            
        elif isMemory:
            self.memories_counted += 1
            
        else:
            self.broadcasts_observed += interaction['total']['count']
            self.cycles_observed += interaction.cycles_present
        
        for trait in interaction.trait_guesses:
            if trait not in self.perceived_traits:
                self.perceived_traits[trait] = interaction.trait_guesses[trait]
                
            else:
                self.perceived_traits[trait] = \
                    combineAverages(self.perceived_traits[trait], self.interaction_count, \
                    interaction.trait_guesses[trait], 1)
		
        self.interaction_count += 1
        self.updateRating(owner)
        
    # get % desirability from traits and contacts, calc rating relative to 
    # regard lower/upper bounds
    def updateRating(self, owner):
        avg_rating = averageContainer()
        for trait in self.perceived_traits:
            trait_delta = abs(owner.getDesired(trait) - self.perceived_traits[trait])
            trait_rating = 99.0 - trait_delta
            
            trait_priority = owner.desire_priority[trait]
            
            avg_rating.addAverage(trait_rating, trait_priority)
        
	    self.rating = avg_rating.average
        
    def getPerceivedOffset(self, trait, other):
        if str(other) != self.other_ID:
            raise Exception
            
        delta = abs(other[trait]['base'] - self.perceived_traits[trait])
        return delta
        
    def getDesiredOffset(self, trait, owner):
        if str(owner) != self.owner_ID:
            raise Exception("owner_ID does not matched owner passed")
            
        delta = abs(owner.d_traits[trait]['base'] - self.perceived_traits[trait])
        return delta
        
    def getAveragePerceivedOffset(self, other):
        offset_list = list()
        for trait in self.perceived_traits:
            trait_offset = self.getPerceivedOffset(trait, other)
            offset_list.append(trait_offset)
            
        return listAverage(offset_list)
        
    def getAverageDesiredOffset(self, owner):
        offset_list = list()
        for trait in self.perceived_traits:
            trait_offset = self.getDesiredOffset(trait, owner)
            offset_list.append(trait_offset)
            
        return listAverage(offset_list)
