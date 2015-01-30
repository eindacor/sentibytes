from sb_utilities import getCoefficient, calcInfluence, calcAccuracy, \
    boundsCheck, combineAverages, valueState, listAverage, averageContainer

class perception(object):
    def __init__(self, other_ID, owner):
        self.other_ID = other_ID
        self.owner_ID = owner.sentibyte_ID
        self.interaction_count = 0
        self.broadcasts_observed = 0
        self.cycles_observed = 0
        self.rumors_heard = 0
        self.memories_counted = 0
        
        self.avg_actual_offset = averageContainer()
        self.avg_desired_offset = averageContainer()
        # interaction and instance ratings are for monitoring purposes only, 
        # they do not affect overall rating directly
        self.avg_interaction_rating = averageContainer()
        self.avg_instance_rating = averageContainer()
        
        self.overall_rating = averageContainer()
        self.overall_rating.addValue(owner['regard']['current'])
        
        # trust level will eventually override proc('trusting') in communication
        self.trust = 0.0
            
        # deprecated
        '''
        # regard coefficient must be inverted. higher regard means assumed value
        # will be closer to what the owner desires
        inverted_regard_coefficient = 1 - owner['regard']['coefficient']
        for trait in owner.d_traits:
            desired_value = owner.getDesired(trait)
            assumed_value = calcAccuracy(desired_value, inverted_regard_coefficient, max_offset=20)
            self.perceived_traits[trait] = assumed_value
            
        self.updateRating(owner)
        '''
    
    def __eq__(self, other):
        return self.overall_rating.average == other.overall_rating.average
        
    def __ne__(self, other):
        return self.overall_rating.average != other.overall_rating.average
    
    def __lt__(self, other):
        return self.overall_rating.average < other.overall_rating.average
        
    def __le__(self, other):
        return self.overall_rating.average <= other.overall_rating.average
        
    def __gt__(self, other):
        return self.overall_rating.average > other.overall_rating.average
        
    def __ge__(self, other):
        return self.overall_rating.average >= other.overall_rating.average
        
    def addInstance(self, rating):
        self.avg_instance_rating.addValue(rating)
        self.overall_rating.addValue(rating)
            
    def addInteraction(self, interaction, owner, other, isMemory=False, isRumor=False):
        if isRumor:
            self.rumors_heard += 1
            
        elif isMemory:
            self.memories_counted += 1
            
        else:
            self.broadcasts_observed += interaction['total']['count']
            self.cycles_observed += interaction.cycles_present
        
        if interaction.trait_guesses:
            avg_actual_offset = averageContainer()
            avg_desired_offset = averageContainer()
            avg_rating = averageContainer()
            for trait in interaction.trait_guesses:
                guess = interaction.trait_guesses[trait]
                # eliminating calculation for actual offset would greatly reduce
                # processing time
                actual_offset = abs(other[trait]['base'] - guess)
                desired_offset = abs(owner.d_traits[trait]['current'] - guess)
                avg_actual_offset.addValue(actual_offset)
                avg_desired_offset.addValue(desired_offset)
                
                tolerance = owner['tolerance']['current']
                tolerance_delta = boundsCheck(tolerance - desired_offset)
                trait_rating = (tolerance_delta/float(tolerance)) * 100.0
                trait_priority = owner.desire_priority[trait]
                
                avg_rating.addAverage(trait_rating, trait_priority)
            
            self.avg_interaction_rating.addValue(avg_rating.average)  
            self.avg_actual_offset.addValue(avg_actual_offset.average)
            self.avg_desired_offset.addValue(avg_desired_offset.average)
            
            self.overall_rating.addValue(avg_rating.average)
    
    '''   
    # get % desirability from traits and contacts, calc rating relative to 
    # regard lower/upper bounds
    def updateRating(self, owner):
        avg_rating = averageContainer()
        for trait in self.perceived_traits:
            trait_delta = abs(owner.getDesired(trait) - self.perceived_traits[trait])
            tolerance = owner['tolerance']['current']
            tolerance_delta = tolerance - trait_delta
            trait_rating = (tolerance_delta/float(tolerance)) * 100.0
            
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
    '''
