from sb_sentibyte import sentibyte
from sb_utilities import valueState
import subprocess
from os import path

def linesFromFile(file_name):
    file = open(file_name, 'r')
    lines = file.readlines()
    file.close()
    
    for i in range(len(lines)):
        lines[i] = lines[i].replace('\n', '')
        lines[i] = lines[i].replace(' ', '')
        lines[i] = lines[i].partition('$')[0]
    
    lines = [line for line in lines if line != '']
    
    return lines
    
def dissectString(target, dissector):
    separated = list()
    toAdd = ''
    
    for i in range(len(target)):
        if target[i] != dissector: 
            toAdd += target[i]
        
        if target[i] == dissector or i == len(target) - 1:
            separated.append(toAdd)
            toAdd = ''
            
    return separated

def traitsFromConfig(config_file):
    lines = linesFromFile(config_file)
    
    p_traits = {}
    i_traits = {}
    d_traits = {}
    
    for line in lines:
        components = line.partition('=')
            
        values = dissectString(components[2], ',')
        value_min = float(values[0])
        value_max = float(values[1])
        
        trait = components[0]
        trait = trait[2:]
        
        if 'p_' in components[0]:
            p_traits[trait] = valueState(value_min, value_max)
        elif 'i_' in components[0]:
            i_traits[trait] = valueState(value_min, value_max)
        elif 'd_' in components[0]:
            d_traits[trait] = valueState(value_min, value_max)
        
    return [p_traits, i_traits, d_traits]
        
def traitsFromFile(sb_file): 
    lines = linesFromFile(sb_file)
    
    p_traits = {}
    i_traits = {}
    d_traits = {}
    
    for line in lines:
        components = line.partition('=')
        
        values = dissectString(components[2], ',')
        value_min = float(values[0])
        value_base = float(values[1])
        value_max = float(values[2])
        
        trait = components[0]
        trait = trait[2:]
        
        temp_vs = valueState()
        temp_vs.params['lower'] = value_min
        temp_vs.params['base'] = value_base
        temp_vs.params['current'] = value_base
        temp_vs.params['upper'] = value_max
        temp_vs.update()
        
        if 'p_' in components[0]:
            p_traits[trait] = temp_vs
        elif 'i_' in components[0]:
            i_traits[trait] = temp_vs
        elif 'd_' in components[0]:
            d_traits[trait] = temp_vs
        
    return [p_traits, i_traits, d_traits]