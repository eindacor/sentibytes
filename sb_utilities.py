from random import randint, choice,  uniform
import random
from jep_loot.jeploot import catRoll, booRoll

def getCoefficient(base_level=0.0, max_level=1.0):
    difference = max_level - base_level
    return base_level + (random.random() * difference)

# returns the desired increment of change based on value passed and coefficient
def calcInfluence(starting, influence, coefficient):
    delta = influence - starting
    return delta * coefficient
    
# returns new value within a range based on range coefficient
def calcAccuracy(value, range_coefficient):
    margain = 10 * range_coefficient * random.random()
    new_value = value + (margain * choice((1, -1)))
    if new_value > 99:
        new_value = 99
        
    elif new_value < 0:
        new_value = 0
        
    return new_value
    
def boundsCheck(value):
    if value > 99:
        return float(99)
        
    elif value < 0:
        return float(0)
        
    else:
        return value
    
# calculates an average based on current average, previous entry count,
# new average, and new entry count
def weightedAverage(initial_avg, prevoius_count, added_avg, added_count):
    new_count = prevoius_count + added_count
    new_avg = (initial_avg * prevoius_count) + (added_avg * added_count)
    return float(new_avg/new_count)
   
# swaps a random character with '$' in a line
# if no characters are present, it will return '$' as a string
def distortLine(line):
    if line.count('$') == len(line) and len(line) < 10:
        return line + '$'
    
    index_insert = 0
    new_line = ''
    
    if len(line) == 0:
        new_line += '$'
        
    else:
        index_insert = randint(0, len(line))
    
        for i in range(len(line)):
            if i == index_insert:
                new_line += '$'
                
            else:
                new_line += line[i]
            
    return new_line
   
# valueState objects contain a range of values known as 'min' and 'max'
# within the min and max exists a 'base'
class valueState(object):
    def __init__(self, lower_min=0.0, upper_max=99.0):
        self.params = {}
        span = boundsCheck(upper_max) - boundsCheck(lower_min)
        self.setBounds(boundsCheck(lower_min), span)
        self.setBase()
        self.params['current'] = float(self['base'])
        # fluct_c determines size of fluctuations relative to upper - lower
        self.fluct_c = getCoefficient(.02, .05)
        # sensitivity determines how much level is affected by outside influences
        self.sensitivity = getCoefficient(.02, .2)
        
        self.update()
        
    def __getitem__(self, index):
        return self.params[index]
        
    def __eq__(self, other):
        return int(self.params['current']) == int(other.params['current'])
        
    def __ne__(self, other):
        return int(self.params['current']) != int(other.params['current'])
        
    def duplicate(self):
        new_vs = valueState()
        
        new_vs.params = self.params.copy()
        new_vs.fluct_c = self.fluct_c
        new_vs.sensitivity = self.sensitivity

        return new_vs
        
    def update(self):
        delta = self['current'] - self['lower']
        value_range = self['upper'] - self['lower']
        self.params['relative'] = delta / value_range
        self.params['coefficient'] = float(self['current']) / 100.0
        
    # increases/decreases 'current' parameter based on input and sensitivity
    def influence(self, value, coefficient=-1):
        if coefficient == -1:
            coefficient=self.sensitivity
            
        value_change = calcInfluence(self['current'], value, coefficient)
        self.params['current'] = self['current'] + value_change
        
        self.update()
        
    # returns true based on the coefficient of the current value
    # a current value of 75 has a 75% chance to return true
    def proc(self):
        self.update()
        return random.random() < self['coefficient']
    
    # initializes valueState bounds    
    def setBounds(self, lower_min, span):
        probability_weight = [18, 20, 24, 20, 18]
        
        lower_quadrants = {}
        lower_quadrants[(lower_min + (.0 * span), lower_min + (.1 * span))] = probability_weight[0]
        lower_quadrants[(lower_min + (.1 * span), lower_min + (.2 * span))] = probability_weight[1]
        lower_quadrants[(lower_min + (.2 * span), lower_min + (.3 * span))] = probability_weight[2]
        lower_quadrants[(lower_min + (.3 * span), lower_min + (.4 * span))] = probability_weight[3]
        lower_quadrants[(lower_min + (.4 * span), lower_min + (.5 * span))] = probability_weight[4]
        lower_bound_quadrant = catRoll(lower_quadrants)
        self.params['lower'] = uniform(lower_bound_quadrant[0], lower_bound_quadrant[1])
        
        upper_quadrants = {}
        upper_quadrants[(lower_min + (.5 * span), lower_min + (.6 * span))] = probability_weight[0]
        upper_quadrants[(lower_min + (.6 * span), lower_min + (.7 * span))] = probability_weight[1]
        upper_quadrants[(lower_min + (.7 * span), lower_min + (.8 * span))] = probability_weight[2]
        upper_quadrants[(lower_min + (.8 * span), lower_min + (.9 * span))] = probability_weight[3]
        upper_quadrants[(lower_min + (.9 * span), lower_min + span)] = probability_weight[4]
        upper_bound_quadrant = catRoll(upper_quadrants)
        self.params['upper'] = uniform(upper_bound_quadrant[0], upper_bound_quadrant[1])
     
    # initializes valueState 'base' parameter   
    def setBase(self):
        probability_weight = [18, 20, 24, 20, 18]
        
        span = self['upper'] - self['lower']
        low = self['lower'] + (span * .1)
        span -= (span * .2)
        
        base_quadrants = {}
        base_quadrants[(low + (.0 * span), low + (.2 * span))] = probability_weight[0]
        base_quadrants[(low + (.2 * span), low + (.4 * span))] = probability_weight[1]
        base_quadrants[(low + (.4 * span), low + (.6 * span))] = probability_weight[2]
        base_quadrants[(low + (.6 * span), low + (.8 * span))] = probability_weight[3]
        base_quadrants[(low + (.8 * span), low + span)] = probability_weight[4]
        base_quadrant = catRoll(base_quadrants)
        self.params['base'] = uniform(base_quadrant[0], base_quadrant[1])
        
    # Randomly increases or decreases the 'current' parameter. The likelihood
    # of 'current' increasing or decreasing depends on its relative position to 
    # the 'base' parameter.
    def fluctuate(self):
        positive_chance = float(0)
        
        # determine chance of increasing/decreasing based on current relative
        # to base level
        if self['current'] >= self['base']:
            dist_from_upper = self['upper'] - self['current']
            upper_range = self['upper'] - self['base']
            positive_chance = (dist_from_upper/upper_range) * .5
            
        else:
            dist_from_lower = self['current'] - self['lower']
            lower_range = self['base'] - self['lower']
            positive_chance = 1 - ((dist_from_lower/lower_range) * .5)
            
        value_change = self.fluct_c * (self['upper'] - self['lower'])
        
        if not booRoll(positive_chance):
            value_change *= -1
            
        self.params['current'] = self.params['current'] + value_change

        if self['current'] > self['upper']:
            self.params['current'] = float(self['upper'])
                
        elif self['current'] < self['lower']:
            self.params['current'] = float(self['lower'])
            
        self.update()