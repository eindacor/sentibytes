from sb_sentibyte import sentibyte
from sb_utilities import currentTime
from sb_communication import community
import subprocess
from sys import argv, executable
from sb_fileman import traitsFromConfig, traitsFromFile, loadPremadeSBs, getTruth, createRandomSBs
from os import path
import random
from sb_datalog import updateSBData, updateSummary, updateStatusLog

random.seed()

the_truth = getTruth()

test_community = community()
# load premade sentibytes from ./sb_files 
premade_sentibytes = loadPremadeSBs(the_truth)
for sb in premade_sentibytes:
    test_community.addMember(sb)
    
# generate specified number of random sentibytes 
population_count = 20
random_sentibytes = createRandomSBs(population_count, the_truth)
for sb in random_sentibytes:
    test_community.addMember(sb)

time_string = currentTime()

script_location = path.dirname(path.abspath('__file__'))
sb_data = script_location + '/sb_datalog/' + time_string + "_sb_data.txt"
sb_summary = script_location + '/sb_datalog/' + time_string + "_summary.txt"
sb_status = script_location + '/sb_datalog/' + time_string + "_status_log.txt"
config_file = script_location + '/traits_config.txt'

status_log_lines = list()

turns = 1000
try:
    for i in range(turns):
        if i % 50==0 and i != 0:
            updateSummary(test_community, config_file, sb_summary, the_truth)
            
        status_log_lines += test_community.cycle()
        
    updateSummary(test_community, config_file, sb_summary, the_truth)
    updateSBData(test_community, sb_data)
    updateStatusLog(sb_status, status_log_lines)

except KeyboardInterrupt:
    print "finalizing log file"
    updateSummary(test_community, config_file, sb_summary, the_truth)
