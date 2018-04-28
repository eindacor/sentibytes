from sb_utilities import valueState, dissectString
import subprocess, platform, pickle
from os import path
from sys import executable

def getPath():
    return path.dirname(path.abspath('__file__'))
    
def getTruth():
    truthfile = open(getPath() + "/sb_sentibyte.py", 'r')
    truth_lines = truthfile.readlines()
    the_truth = {}
    for i in range(len(truth_lines)):
        the_truth[i] = truth_lines[i]
        
    truthfile.close()
    return the_truth

def getListOfFiles(target_path):
    if platform.system() == 'Windows':
        output = subprocess.Popen([executable, 'ls', target_path], stdout=subprocess.PIPE)
    else:
        output = subprocess.Popen(['ls', target_path], stdout=subprocess.PIPE)
        
    files_present = output.stdout.readlines()
    for i in range(len(files_present)):
        files_present[i] = files_present[i].replace('\n', '')
        
    return files_present

def writeLines(lines, file):

    for i in range(len(lines)):
        file.write(lines[i] + '\n')
        
    file.close()

# Converts text documents into a list of lines, removing endline chars,
# empty lines, and anything after '$' symbol
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

# Returns a list of trait dictionaries. Each dictionary contains traits as keys,
# and valueStates as their values. The returning list is used to initialize
# sentibytes.
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
            d_traits[trait] = valueState(value_min, value_max)
        
    return [p_traits, i_traits, d_traits]
  
# Returns a list of trait dictionaries. Each dictionary contains traits as keys,
# and valueStates as their values. All values are based on information from a 
# text file. The returning list is used to initialize sentibytes.      
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
    
def readSB(sb_ID, community=None):
    sb_file = getPath() + '/sb_data/' + sb_ID + '.sb'
    file = open(sb_file, 'rb')
    sb = pickle.load(file)
    sb.community = community
    if sb.current_session_ID and community:
        sb.current_session = community.getSession(sb.current_session_ID)
    file.close()
    return sb
    
def writeSB(sb):
    sb_file = getPath() + '/sb_data/' + sb.sentibyte_ID + '.sb'
    sb.community = None
    if sb.current_session:
        sb.current_session = None
    file = open(sb_file, 'wb')
    pickle.dump(sb, file)
    file.close()
    
def cleanup():
    sb_file_path = getPath() + '/sb_data'
    file_list = getListOfFiles(sb_file_path)

    for file in file_list:
        if platform.system() == 'Windows':
            output = subprocess.Popen([executable, 'rm', sb_file_path + '/' + file])
        else:
            subprocess.Popen(['rm', sb_file_path + '/' + file])
    
        
