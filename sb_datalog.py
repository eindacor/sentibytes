from sb_parser import linesFromFile

def writeLines(lines, file):

    for i in range(len(lines)):
        file.write(lines[i] + '\n')
        
    file.close()

def updateSBData(community, sb_data_file, traits=True, friends=True):
    file = open(sb_data_file, 'w')
    file = open(sb_data_file, 'a')
    
    member_info = list()
    for member in community.members:
        member_info.append("----------------------")
        for line in member.getInfo(traits=True, friends=True):
            member_info.append(line)
                
    writeLines(member_info, file)
    file.close()

def updateSummary(community, config_file, sb_summary_file):
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
    
    stats.append("---------------------")
    stats.append("Config file:")
    
    config_lines = linesFromFile(config_file)
    
    stats += config_lines
    
    file = open(sb_summary_file, 'w')
    file = open(sb_summary_file, 'a')
    
    writeLines(stats, file)
    
    file.close()