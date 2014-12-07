from random import randint, choice
import random

def newAverage(prev_count, prev_average, value):
    total = (prev_count * prev_average) + value
    count = prev_count + 1
    return total/count
    
def getCoefficient(base_level, max_level):
    difference = max_level - base_level
    return base_level + (random.random() * difference)
    
def calcInfluence(starting, influence, coefficient):
    delta = influence - starting
    return delta * coefficient
    
# returns new value based on range coefficient
def calcAccuracy(value, range_coefficient):
    margain = 10 * range_coefficient * random.random()
    new_value = value + margain * choice((1, -1))
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
        
def weightedAverage(first, first_count, second, second_count):
    total_count = first_count + second_count
    total = (first * first_count) + (second * second_count)
    return float(total/total_count)