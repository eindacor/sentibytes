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
    
    member_info = list()
    for member in community.members:
        member_info.append("----------------------")
        for line in member.getInfo(traits=True, friends=True):
            member_info.append(line)
                
    writeLines(member_info, file)
    file.close()
   
    total_knowledge = 0
    total_learned_from_others = 0
    total_learned_on_own = 0
    total_ratings = 0
    rating_count = 0.0
    total_relative_ratings = 0
    relative_rating_count = 0.0
    total_rating_friends = 0
    rating_friends_count = 0.0
    total_relative_ratings_friends = 0
    relative_rating_friends_count = 0.0
    total_inv_to_strangers = 0
    total_inv_to_contacts = 0
    total_inv_to_friends = 0
    total_met = 0
    total_met_through_others = 0
    highest_relative_rating = 0
    lowest_relative_rating = 99
    mem_count = float(len(community.members))
    for member in community.members:
        total_knowledge += len(member.knowledge)
        total_learned_from_others += member.learned_from_others
        total_learned_on_own += member.learned_on_own
        for other in member.contacts:
            if member.getRating(other, relative=True) > highest_relative_rating:
                highest_relative_rating = member.getRating(other, relative=True)
            elif member.getRating(other, relative=True) < lowest_relative_rating:
                lowest_relative_rating = member.getRating(other, relative=True)
            total_ratings += member.getRating(other)
            rating_count += 1
            total_relative_ratings += member.getRating(other, relative=True)
            relative_rating_count += 1
        for other in member.friend_list:
            total_rating_friends += member.getRating(other)
            rating_friends_count += 1
            total_relative_ratings_friends += member.getRating(other, relative=True)
            relative_rating_friends_count += 1
        total_inv_to_strangers += member.invitaitons_to_strangers
        total_inv_to_contacts += member.invitations_to_contacts
        total_inv_to_friends += member.invitations_to_friends
        total_met += len(member.contacts)
        total_met_through_others += member.met_through_others
    
    avg_knowledge = total_knowledge/mem_count
    avg_learned_from_others = total_learned_from_others/mem_count
    avg_learned_on_own = total_learned_on_own/mem_count
    avg_ratings = total_ratings/rating_count
    avg_relative_ratings = total_relative_ratings/relative_rating_count
    avg_rating_friends = total_rating_friends/rating_friends_count
    avg_relative_ratings_friends = total_relative_ratings_friends/relative_rating_friends_count
    avg_inv_to_strangers = total_inv_to_strangers/mem_count
    avg_inv_to_contacts = total_inv_to_contacts/mem_count
    avg_inv_to_friends = total_inv_to_friends/mem_count
    avg_met = total_met/mem_count
    avg_met_through_others = total_met_through_others/mem_count
    
    stats = list()
    
    stats.append("members: %d" % mem_count)
    stats.append("cycles: %d" % community.current_cycle)
    stats.append("average knowledge: %f" % avg_knowledge)
    stats.append("average learned from others: %f" % avg_learned_from_others)
    stats.append("average learned on own: %f" % avg_learned_on_own)
    stats.append("average relative rating: %f" % avg_relative_ratings)
    stats.append("average relative rating of friends: %f" % avg_relative_ratings_friends)
    stats.append("average invitations to strangers: %f" % avg_inv_to_strangers)
    stats.append("average invitations to contacts: %f" % avg_inv_to_contacts)
    stats.append("average invitations to friends: %f" % avg_inv_to_friends)
    stats.append("average others met: %f" % avg_met)
    stats.append("average met through others: %f" % avg_met_through_others)
    stats.append("highest relative rating: %f" % highest_relative_rating)
    stats.append("lowest relative rating: %f" % lowest_relative_rating)
    
    file = open("summary.txt", 'w')
    file = open("summary.txt", 'a')
    
    writeLines(stats, file)
    
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

turns = 100000

try:
    for i in range(turns):
        if i % 50==0 and i != 0:
            updateLog(test_community)
        test_community.cycle()
        
    updateLog(test_community)

except:
    print "finalizing log file"
    updateLog(test_community)
