from sb_sentibyte import sentibyte
from sb_communication import community
import subprocess
from sys import argv, executable
from sb_parser import traitsFromConfig, traitsFromFile
from os import path, system
import random
from sb_datalog import updateSBData, updateSummary
from datetime import datetime

random.seed()

test_community = community()

truthfile = open("sb_sentibyte.py", 'r')
truth_lines = truthfile.readlines()
the_truth = {}
for i in range(len(truth_lines)):
    the_truth[i] = truth_lines[i]

script_location = path.dirname(path.abspath(__file__))

# create sentibytes from files in sb_files directory
output = subprocess.Popen(['ls', script_location + '/sb_files'], stdout=subprocess.PIPE)
files_present = output.stdout.readlines()
for i in range(len(files_present)):
    files_present[i] = files_present[i].replace('\n', '')

for file_name in files_present:
    full_path = script_location + '/sb_files/' + file_name
    traits = traitsFromFile(full_path)
    test_community.addMember(sentibyte(file_name, the_truth, traits))
    
config_file = script_location + '/traits_config.txt'

# add X random sb's to community
num_names = 10
member_counter = 0
namefile = open(script_location + '/names.txt')
for i, line in enumerate(namefile):
    if i % (4946 / num_names) == 0:
        name = line.replace('\n', '')
        traits = traitsFromConfig(config_file)
        test_community.addMember(sentibyte(name, the_truth, traits))
        member_counter += 1
        
    if member_counter == num_names:
        break
    
namefile.close()

turns = 100000

current = datetime.now()

time_string = ''

time_string += str(current.year)
if int(current.month) < 10:
    time_string += '0'
time_string += str(current.month)
if int(current.day) < 10:
    time_string += '0'
time_string += str(current.day)
if int(current.hour) < 10:
    time_string += '0'
time_string += str(current.hour)
if int(current.minute) < 10:
    time_string += '0'
time_string += str(current.minute)

sb_data = script_location + '/sb_datalog/' + time_string + "_sb_data.txt"
sb_summary = script_location + '/sb_datalog/' + time_string + "_summary.txt"

try:
    for i in range(turns):
        if i % 50==0 and i != 0:
            updateSummary(test_community, config_file, sb_summary, the_truth)
            
        #if i % 1000 == 0 and i != 0:
            #updateSBData(test_community, sb_data)
        test_community.cycle()
        
    updateSummary(test_community, config_file, sb_summary, the_truth)
    updateSBData(test_community, sb_data)

except:
    print "finalizing log file"
    updateSummary(test_community, config_file, sb_summary, the_truth)
