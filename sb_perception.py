from sb_utilities import getCoefficient, calcInfluence, calcAccuracy, \
    boundsCheck, valueState, listAverage, averageContainer

class perception(object):
    def __init__(self, other_ID, owner):
        self.other_ID = other_ID
        self.owner_ID = owner.sentibyte_ID
        self.interaction_count = 0
        self.broadcasts_observed = 0
        self.cycles_observed = 0
        self.rumors_heard = 0
        self.memories_counted = 0
        
        self.avg_desired_offset = averageContainer()
        # interaction and instance ratings are for monitoring purposes only, 
        # they do not affect overall rating directly
        self.avg_interaction_rating = averageContainer()
        self.avg_instance_rating = averageContainer()
        
        self.overall_rating = averageContainer()
        self.overall_rating.addValue(owner['regard']['current'])
        
        # trust level will eventually override proc('trusting') in communication
        self.trust = 0.0
    
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
        
    def addInstance(self, weight):
        rating = boundsCheck(self.overall_rating.average + weight)
        self.avg_instance_rating.addValue(rating)
        self.overall_rating.addValue(rating)
            
    def addInteraction(self, interaction, owner, isMemory=False, isRumor=False):
        if isRumor:
            self.rumors_heard += 1
            
        elif isMemory:
            self.memories_counted += 1
            
        else:
            self.broadcasts_observed += interaction['total']['count']
            self.cycles_observed += interaction.cycles_present
        
        if interaction.trait_guesses:
            avg_desired_offset = averageContainer()
            avg_rating = averageContainer()
            for trait in interaction.trait_guesses:
                guess = interaction.trait_guesses[trait]
                # eliminating calculation for actual offset would greatly reduce
                # processing time
                desired_offset = abs(owner.d_traits[trait]['current'] - guess)
                avg_desired_offset.addValue(desired_offset)
                
                tolerance = owner['tolerance']['current']
                tolerance_delta = boundsCheck(tolerance - desired_offset)
                trait_rating = (tolerance_delta/float(tolerance)) * 100.0
                trait_priority = owner.desire_priority[trait]
                
                avg_rating.addAverage(trait_rating, trait_priority)
            
            self.avg_interaction_rating.addValue(avg_rating.average)  
            self.avg_desired_offset.addValue(avg_desired_offset.average)
            
            self.overall_rating.addValue(avg_rating.average)