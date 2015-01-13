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

def updateSummary(community, config_file, sb_summary_file, the_truth):
    total_knowledge = 0
    total_false_knowledge = 0
    most_accurate_knowledge = 0
    least_accurate_knowledge = len(the_truth)
    total_learned_from_others = 0
    total_learned_on_own = 0
    total_ratings = 0
    total_avg_offset = 0
    total_avg_offset_friends = 0
    total_relative_ratings = 0
    contact_count = 0.0
    total_rating_friends = 0
    total_relative_ratings_friends = 0
    friend_count = 0.0
    total_sociable_procs = 0
    total_cycles_alone = 0
    total_cycles_in_session = 0
    total_inv_to_strangers = 0
    total_inv_to_contacts = 0
    total_inv_to_friends = 0
    total_entries_of_contacts = 0
    total_entries_of_friends = 0
    total_interactions_with_contacts = 0
    total_interactions_with_friends = 0
    total_failed_connection_attempts = 0
    total_successful_connection_attempts = 0
    total_met = 0
    total_met_through_others = 0
    highest_relative_rating = 0
    lowest_relative_rating = 99
    mem_count = float(len(community.members))
    for member in community.members:
        total_knowledge += len(member.knowledge)
        accurate_knowledge = 0
        for index in member.knowledge.keys():
            if member.knowledge[index] != the_truth[index]:
                total_false_knowledge += 1
                
            else:
                accurate_knowledge += 1
                
        if accurate_knowledge > most_accurate_knowledge:
            most_accurate_knowledge = accurate_knowledge
            
        if accurate_knowledge < least_accurate_knowledge:
            least_accurate_knowledge = accurate_knowledge
        
        total_learned_from_others += member.learned_from_others
        total_learned_on_own += member.learned_on_own
        for other in member.contacts:
            if member.getRating(other, relative=True) > highest_relative_rating:
                highest_relative_rating = member.getRating(other, relative=True)
            elif member.getRating(other, relative=True) < lowest_relative_rating:
                lowest_relative_rating = member.getRating(other, relative=True)
            total_ratings += member.getRating(other)
            contact_count += 1
            total_relative_ratings += member.getRating(other, relative=True)
            total_entries_of_contacts += member.perceptions[other].entries
            total_interactions_with_contacts += member.perceptions[other].interaction_count
            if member.getPerceptionOffset(other) != 'n/a':
                total_avg_offset += member.getPerceptionOffset(other)
        for other in member.friend_list:
            total_rating_friends += member.getRating(other)
            friend_count += 1
            total_relative_ratings_friends += member.getRating(other, relative=True)
            total_avg_offset_friends += member.getPerceptionOffset(other)
            total_entries_of_friends += member.perceptions[other].entries
            total_interactions_with_friends += member.perceptions[other].interaction_count
        total_sociable_procs += member.sociable_count
        total_inv_to_strangers += member.invitaitons_to_strangers
        total_inv_to_contacts += member.invitations_to_contacts
        total_inv_to_friends += member.invitations_to_friends
        total_met += len(member.contacts)
        total_met_through_others += member.met_through_others
        total_failed_connection_attempts += member.failed_connection_attempts
        total_successful_connection_attempts += member.successful_connection_attempts
        total_cycles_in_session += member.cycles_in_session
        total_cycles_alone += member.cycles_alone
    
    avg_knowledge = total_knowledge/mem_count
    avg_false_knowledge = total_false_knowledge/mem_count
    avg_learned_from_others = total_learned_from_others/mem_count
    avg_learned_on_own = total_learned_on_own/mem_count
    avg_ratings = total_ratings/contact_count
    avg_relative_ratings = total_relative_ratings/contact_count
    avg_rating_friends = total_rating_friends/friend_count
    avg_relative_ratings_friends = total_relative_ratings_friends/friend_count
    avg_avg_offset = total_avg_offset/contact_count
    avg_avg_offset_friends = total_avg_offset_friends/friend_count
    avg_sociable_procs = total_sociable_procs/mem_count
    avg_cycles_in_session = total_cycles_in_session/mem_count
    avg_cycles_alone = total_cycles_alone/mem_count
    avg_inv_to_strangers = total_inv_to_strangers/mem_count
    avg_inv_to_contacts = total_inv_to_contacts/mem_count
    avg_inv_to_friends = total_inv_to_friends/mem_count
    avg_failed_connection_attempts = total_failed_connection_attempts/mem_count
    avg_successful_connection_attempts = total_successful_connection_attempts/mem_count
    avg_entries_of_contacts = total_entries_of_contacts/contact_count
    avg_entries_of_friends = total_entries_of_friends/friend_count
    avg_interactions_with_contacts = total_interactions_with_contacts/contact_count
    avg_interactions_with_friends = total_interactions_with_friends/friend_count
    avg_met = total_met/mem_count
    avg_met_through_others = total_met_through_others/mem_count
    
    stats = list()
    
    stats.append("members: %d" % mem_count)
    stats.append("cycles: %d" % community.current_cycle)
    stats.append("available knowledge: %d" % len(the_truth))
    stats.append("average knowledge: %f" % avg_knowledge)
    stats.append("average false knowledge: %f" % avg_false_knowledge)
    stats.append("most accurate knowledge: %d" % most_accurate_knowledge)
    stats.append("least accurate knowledge: %d" % least_accurate_knowledge)
    stats.append("average learned from others: %f" % avg_learned_from_others)
    stats.append("average learned on own: %f" % avg_learned_on_own)
    stats.append("average relative rating: %f" % avg_relative_ratings)
    stats.append("average relative rating of friends: %f" % avg_relative_ratings_friends)
    stats.append("average perception offset: %f" % avg_avg_offset)
    stats.append("average perception offset of friends: %f" % avg_avg_offset_friends)
    stats.append("average cycles alone: %f" % avg_cycles_alone)
    stats.append("average cycles in session: %f" % avg_cycles_in_session)
    stats.append("average sociable proc count: %f" % avg_sociable_procs)
    stats.append("average failed connection attempts: %f" % avg_failed_connection_attempts)
    stats.append("average successful connection attempts: %f" % avg_successful_connection_attempts)
    stats.append("average invitations to strangers: %f" % avg_inv_to_strangers)
    stats.append("average invitations to contacts: %f" % avg_inv_to_contacts)
    stats.append("average invitations to friends: %f" % avg_inv_to_friends)
    stats.append("average entries for contacts: %f" % avg_entries_of_contacts)
    stats.append("average entries for friends: %f" % avg_entries_of_friends)
    stats.append("average # of interactions with contacts: %f" % avg_interactions_with_contacts)
    stats.append("average # of interactions with friends: %f" % avg_interactions_with_friends)
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