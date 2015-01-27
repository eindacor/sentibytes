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

run_on_memory = False
if platform.system() == 'Windows':
    population_count = 1000
            
else:
    population_count = 180
    
cycles = 1000
update_frequency = 10

if len(argv) > 1:
    for i in range(len(argv)):
        # -m flag makes program run on memory only
        if argv[i] == '-m':
            run_on_memory = True
            
        if 'pop=' in argv[i]:
            pop_string = argv[i].replace('pop=', '')
            if int(pop_string) < 0:
                raise Exception('population cannot be negative')
            population_count = int(pop_string)
            
        if 'cycles=' in argv[i]:
            cycle_string = argv[i].replace('cycles=', '')
            if int(cycle_string) < 0:
                raise Exception('cycle count cannot be negative')
            cycles = int(cycle_string)
            
        if 'update=' in argv[i]:
            update_string = argv[i].replace('update=', '')
            if int(update_string) < 0:
                raise Exception('update frequency cannot be negative')
            update_frequency = int(update_string)

test_community = community(keep_members_active=run_on_memory)
# load premade sentibytes from ./sb_files 
premade_sentibytes = loadPremadeSBs(the_truth)
for sb_ID in premade_sentibytes:
    test_community.addMember(sb_ID)
   
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

if cycles > 20 or population_count > 20:
    status_tracking = False

else:
    status_tracking = True
    updateStatusLog(sb_status, status_log_lines, True)
    
try:
    for i in range(cycles):
        print "cycle: %d" % i
        if i % update_frequency==0 and i != 0:
            print "......updating summary"
            updateSummary(test_community, config_file, sb_summary, the_truth)

        status_lines = test_community.cycle()

        if status_tracking:
            updateStatusLog(sb_status, status_lines, False)
     
    print "......updating summary"   
    updateSummary(test_community, config_file, sb_summary, the_truth)
    updateSBData(test_community, sb_data)
        
    cleanup()

except KeyboardInterrupt:
    print "......updating summary"
    updateSummary(test_community, config_file, sb_summary, the_truth)
    cleanup()
