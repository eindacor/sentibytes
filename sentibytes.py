from sb_sentibyte import sentibyte
from sb_communication import community
import subprocess
from sys import argv
from sb_parser import generateSentibyte
from os import path
import random

random.seed()

def pageBreak(title):
    print "-" * 40
    print title
    print "-" * 40

test_community = community()

truthfile = open("sb_sentibyte.py", 'r')
truth_lines = truthfile.readlines()
the_truth = {}
for i in range(len(truth_lines)):
    the_truth[i] = truth_lines[i]

if len(argv) == 1:
    output = subprocess.Popen(['ls', './sb_files'], stdout=subprocess.PIPE)
    files_present = output.stdout.readlines()
    for i in range(len(files_present)):
        files_present[i] = files_present[i].replace('\n', '')
    
    script_location = path.dirname(path.abspath(__file__))
    
    for file in files_present:
        full_path = script_location + '/sb_files/' + file
        test_community.addMember(generateSentibyte(full_path, the_truth))

if len(argv) > 1 and argv[1] == 'random':
    num_names = 120
    
    namefile = open("names.txt")
    for i, line in enumerate(namefile):
        if i % (4946 / num_names) == 0:
            name = line.replace('\n', '')
            test_community.addMember(sentibyte(name, the_truth))
    namefile.close()
    
pageBreak('START')
test_community.printMembers(traits=False, memory=False, perceptions=False, friends=False)

turns = 1000

for i in range(turns):
    if i == turns/2:
        pageBreak('MIDPOINT')
        test_community.printMembers(traits=False, memory=False, perceptions=False)
    test_community.cycle()
        
pageBreak('END')

for member in test_community.members:
    member.updateFriends()
test_community.printMembers(traits=True, memory=False, perceptions=False, friends=True)

pageBreak('RELATIONSHIPS')
best_friend1 = None
best_friend2 = None
worst_enemy1 = None
worst_enemy2 = None
best_rating = 0
worst_rating = 200
for member in test_community.members:
    for other in member.memory.keys():
        sb = member.contacts[other]
        rating = sb.getRating(member) + member.getRating(sb)
        
        if rating > best_rating:
            best_friend1 = member
            best_friend2 = sb
            best_rating = rating
            
        if rating < worst_rating:
            worst_enemy1 = member
            worst_enemy2 = sb
            worst_rating = rating
            
print "best friends: %s & %s" % (best_friend1, best_friend2)
best_friend1.perceptions[str(best_friend2)].printPerception()
best_friend2.perceptions[str(best_friend1)].printPerception()

print "worst enemies: %s & %s" % (worst_enemy1, worst_enemy2)
worst_enemy1.perceptions[str(worst_enemy2)].printPerception()
worst_enemy2.perceptions[str(worst_enemy1)].printPerception()

pageBreak('KNOWLEDGE')
smartest = None
dumbest = None
for member in test_community.members:
    if type(smartest) == type(None) or len(member.knowledge) > len(smartest.knowledge):
        smartest = member
        
    if type(dumbest) == type(None) or len(member.knowledge) < len(dumbest.knowledge):
        dumbest = member

print "smartest:"
smartest.printInfo(traits=True, memory=False, perceptions=False, friends=True)
print "dumbest:"
dumbest.printInfo(traits=True, memory=False, perceptions=False, friends=True)

