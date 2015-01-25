from sb_utilities import currentTimeString
from sb_communication import community
from sys import argv, executable
from sb_fileman import getTruth, cleanup
from os import path
import platform, random
from sb_datalog import updateSBData, updateSummary, updateStatusLog
from sb_sentibyte import loadPremadeSBs, createRandomSBs

random.seed()

the_truth = getTruth()

test_community = community(keep_members_active=False)
# load premade sentibytes from ./sb_files 
premade_sentibytes = loadPremadeSBs(the_truth)
for sb_ID in premade_sentibytes:
    test_community.addMember(sb_ID)
    
# generate specified number of random sentibytes 
if platform.system() == 'Windows':
    population_count = 1000
    
else:
    population_count = 100
   
random_sentibytes = createRandomSBs(population_count, the_truth)
for sb_ID in random_sentibytes:
    test_community.addMember(sb_ID)

time_string = currentTimeString()

script_location = path.dirname(path.abspath('__file__'))
sb_data = script_location + '/sb_datalog/' + time_string + "_sb_data.txt"
sb_summary = script_location + '/sb_datalog/' + time_string + "_summary.txt"
sb_status = script_location + '/sb_datalog/' + time_string + "_status_log.txt"
config_file = script_location + '/traits_config.txt'

status_log_lines = list()

cycles = 1000

if cycles > 20 or population_count > 20:
    status_tracking = False

else:
    status_tracking = True
    updateStatusLog(sb_status, status_log_lines, True)
    
try:
    for i in range(cycles):
        if i % 2==0 and i != 0:
            print "cycle: %d" % i
        if i % 24==0 and i != 0:
            print "cycle: %d (updating summary)" % i
            updateSummary(test_community, config_file, sb_summary, the_truth)

        status_lines = test_community.cycle()

        if status_tracking:
                updateStatusLog(sb_status, status_lines, False)
        
    updateSummary(test_community, config_file, sb_summary, the_truth)
    updateSBData(test_community, sb_data)
        
    cleanup()

except KeyboardInterrupt:
    updateSummary(test_community, config_file, sb_summary, the_truth)
    cleanup()
