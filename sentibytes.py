from sb_sentibyte import sentibyte
from sb_communication import community
import subprocess
from sys import argv
from sb_parser import generateSentibyte
from os import path

def pageBreak(title):
    print "-" * 40
    print title
    print "-" * 40

test_community = community()

if len(argv) == 1:
    output = subprocess.Popen(['ls', './sb_files'], stdout=subprocess.PIPE)
    files_present = output.stdout.readlines()
    for i in range(len(files_present)):
        files_present[i] = files_present[i].replace('\n', '')
    
    script_location = path.dirname(path.abspath(__file__))
    
    for file in files_present:
        full_path = script_location + '/sb_files/' + file
        test_community.addMember(generateSentibyte(full_path))

if len(argv) > 1 and argv[1] == 'random':
    num_names = 50
    
    namefile = open("names.txt")
    for i, line in enumerate(namefile):
        if i % (4946 / num_names) == 0:
            name = line.replace('\n', '')
            test_community.addMember(sentibyte(name))
    namefile.close()
    
pageBreak('START')
test_community.printMembers(traits=False, memory=False, perceptions=False)

turns = 1000

for i in range(turns):
    if i == turns/2:
        pageBreak('MIDPOINT')
        test_community.printMembers(traits=False, memory=False, perceptions=False)
    test_community.cycle()
        
pageBreak('END')
test_community.printMembers(traits=True, memory=False, perceptions=False)

pageBreak('RELATIONSHIPS')
best_friend1 = None
best_friend2 = None
worst_enemy1 = None
worst_enemy2 = None
best_rating = 0
worst_rating = 200
for member in test_community.members:
    for other in test_community.getAllOthers(member):
        if str(member) in other.perceptions.keys() and str(other) in member.perceptions.keys():
            rating = other.getRating(member) + member.getRating(other)
            
            if rating > best_rating and member.perceptions[str(other)].entries > 5:
                best_friend1 = member
                best_friend2 = other
                best_rating = rating
                
            if rating < worst_rating and member.perceptions[str(other)].entries > 5:
                worst_enemy1 = member
                worst_enemy2 = other
                worst_rating = rating
            
print "best friends: %s & %s" % (best_friend1, best_friend2)
best_friend1.perceptions[str(best_friend2)].printPerception()
best_friend2.perceptions[str(best_friend1)].printPerception()

print "worst enemies: %s & %s" % (worst_enemy1, worst_enemy2)
worst_enemy1.perceptions[str(worst_enemy2)].printPerception()
worst_enemy2.perceptions[str(worst_enemy1)].printPerception()

