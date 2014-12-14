from sb_sentibyte import sentibyte
from sb_communication import community
import subprocess
from sys import argv
from sb_parser import generateSentibyte
from os import path
import random

random.seed()

def writeLines(lines, file):

    for i in range(len(lines)):
        file.write(lines[i] + '\n')
        
    file.close()

def updateLog(community, traits=True, friends=True):
    file = open("sentibytes.txt", 'w')
    file = open("sentibytes.txt", 'a')
    
    lines_to_file = list()
    for member in community.members:
        lines_to_file.append("------------------------------------------------")
        lines_to_file.append("unique ID: %s" % member.sentibyte_ID)
        lines_to_file.append("name: %s" % member.name)
        lines_to_file.append("acquired knowledge: %d" % len(member.knowledge))
        lines_to_file.append("learned from others: %d" % member.learned_from_others)
        lines_to_file.append("learned on own: %d" % member.learned_on_own)
        lines_to_file.append("others met: %d" % len(member.contacts))
        lines_to_file.append("others met through mutual contacts: %d" % member.met_through_others)
        lines_to_file.append("invitations to strangers: %d" % member.invitaitons_to_strangers)
        lines_to_file.append("invitations to contacts: %d" % member.invitations_to_contacts)
        lines_to_file.append("invitations to friends: %d" % member.invitations_to_friends)
        lines_to_file.append("current session: %s" % member.current_session)
    
        if traits:
            lines_to_file.append("personal traits...")
            for trait in member.p_traits:
                lines_to_file.append("\t%s: %f (%f base)" % (trait, member[trait]['current'], member[trait]['base']))
            lines_to_file.append("interpersonal traits...")
            for trait in member.i_traits:
                lines_to_file.append("\t%s: %f (%f base)" % (trait, member[trait]['current'], member[trait]['base']))
            lines_to_file.append("desired traits...")
            for trait in member.d_traits:
                lines_to_file.append("\t%s: %f (%d priority weight)" % (trait, member.getDesired(trait), member.desire_priority[trait]))
            
        if len(member.friend_list) > 0 and friends:
            lines_to_file.append("friends:")
            for friend in member.friend_list:
                perception = member.perceptions[friend]
                
                regard_range = perception.owner['regard']['upper'] - perception.owner['regard']['lower']
                delta_to_min = perception.rating - perception.owner['regard']['lower']
                relative_rating = (delta_to_min / regard_range) * 99
                lines_to_file.append("\t%s perception of %s: %f (%f relative)" % (perception.owner, perception.perceived, perception.rating, relative_rating))
                lines_to_file.append("\t(%d entries, %d cycles, %d broadcasts)" % (perception.entries, perception.cycles_present, perception.broadcasts))
                lines_to_file.append("\t%s has sent %d invitations to %s)" % (perception.perceived, perception.invitations, perception.owner))
                lines_to_file.append("\t%s has sent %d invitations to %s)" % (perception.owner, perception.contacts['total'], perception.perceived))
                for key in perception.contacts.keys():
                    lines_to_file.append("\t\t%s: %d" % (key, perception.contacts[key]))
            
            for key in perception.p_traits.keys():
                desired = perception.owner.d_traits[key]['base']
                actual = perception.perceived.i_traits[key]['base']
                priority = perception.owner.desire_priority[key]
                lines_to_file.append("\t\t%s: %f (%f desired) (%f actual) (%d priority weight)" % (key, perception.p_traits[key], desired, actual, priority))
            
            entry_list = [i.entries for i in member.perceptions.values()]
            lines_to_file.append("\taverage entries for connections: %f" % (sum(entry_list) / float(len(entry_list))))
                
            rating_list = [member.getRating(i, relative=True) for i in member.perceptions.keys()]
            lines_to_file.append("\taverage rating for connections: %f" % (sum(rating_list) / float(len(rating_list))))
                
    writeLines(lines_to_file, file)
    file.close()

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
    num_names = 256
    
    namefile = open("names.txt")
    for i, line in enumerate(namefile):
        if i % (4946 / num_names) == 0:
            name = line.replace('\n', '')
            test_community.addMember(sentibyte(name, the_truth))
    namefile.close()

turns = 1000

try:
    for i in range(turns):
        if i % 50==0:
            updateLog(test_community)
        test_community.cycle()
        
    updateLog(test_community)

except:
    print "finalizing log file"
    updateLog(test_community)

