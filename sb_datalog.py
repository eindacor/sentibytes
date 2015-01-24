from sb_fileman import linesFromFile, readSB, writeSB

def writeLines(lines, file):

    for i in range(len(lines)):
        file.write(lines[i] + '\n')
        
    file.close()

def updateSBData(community, sb_data_file, traits=True, friends=True):
    file = open(sb_data_file, 'w')
    file = open(sb_data_file, 'a')
    
    member_info = list()
    for member_ID in community.members:
        member = readSB(member_ID, community)
        member_info.append("----------------------")
        member_info += member.getInfo(traits=True, friends=True)
        #for line in member.getInfo(traits=True, friends=True):
            #member_info.append(line)
                
    writeLines(member_info, file)
    file.close()
    
def updateStatusLog(sb_status_file, status_log_lines, overwrite=True):
    if overwrite:
        file = open(sb_status_file, 'w')
        
    file = open(sb_status_file, 'a')
                
    writeLines(status_log_lines, file)
    file.close()

def updateSummary(community, config_file, sb_summary_file, the_truth):
    total_knowledge = 0
    total_false_knowledge = 0
    most_accurate_knowledge = 0
    least_accurate_knowledge = len(the_truth)
    most_knowledge = 0
    least_knowledge = len(the_truth)
    total_learned_from_others = 0
    total_learned_on_own = 0
    total_misled = 0
    total_corrected = 0
    total_ratings = 0
    total_avg_offset = 0
    total_avg_offset_friends = 0
    total_ratings = 0
    contact_count = 0.0
    total_ratings_friends = 0
    friend_count = 0.0
    total_sociable_procs = 0
    total_cycles_alone = 0
    total_cycles_in_session = 0
    total_inv_to_strangers = 0
    total_inv_to_contacts = 0
    total_inv_to_friends = 0
    total_interactions_contacts = 0
    total_interactions_friends = 0
    total_failed_connection_attempts = 0
    total_successful_connection_attempts = 0
    total_succ_conn_contacts = 0
    total_succ_conn_friends = 0
    total_succ_conn_strangers = 0
    total_unsucc_conn_contacts = 0
    total_unsucc_conn_friends = 0
    total_unsucc_conn_strangers = 0
    total_met = 0
    total_met_through_others = 0
    highest_rating = 0
    lowest_rating = 99
    mem_count = float(len(community.members))
    for member_ID in community.members:
        member = readSB(member_ID)
        total_false_knowledge += len(member.false_knowledge)
        total_misled += member.misled_by_others
        total_corrected += member.corrected_by_others

        if len(member.accurate_knowledge) > most_accurate_knowledge:
            most_accurate_knowledge = len(member.accurate_knowledge)
            
        if len(member.accurate_knowledge) < least_accurate_knowledge:
            least_accurate_knowledge = len(member.accurate_knowledge)
        
        member_knowledge_total = len(member.accurate_knowledge) + len(member.false_knowledge)
        total_knowledge += member_knowledge_total
        if member_knowledge_total > most_knowledge:
            most_knowledge = member_knowledge_total
            
        if member_knowledge_total < least_knowledge:
            least_knowledge = member_knowledge_total
        
        total_learned_from_others += member.learned_from_others
        total_learned_on_own += member.learned_on_own
        for other_ID in member.contacts:
            other = readSB(other_ID)
            if member.getRating(other_ID) > highest_rating:
                highest_rating = member.getRating(other_ID)
            elif member.getRating(other_ID) < lowest_rating:
                lowest_rating = member.getRating(other_ID)
            total_ratings += member.getRating(other_ID)
            contact_count += 1
            total_interactions_contacts += member.perceptions[other_ID].interaction_count
            total_avg_offset += member.perceptions[other_ID].getAverageOffset(other)

        for other_ID in member.friend_list:
            other = readSB(other_ID)
            total_ratings_friends += member.getRating(other_ID)
            friend_count += 1
            total_avg_offset_friends += member.perceptions[other_ID].getAverageOffset(other)
            total_interactions_friends += member.perceptions[other_ID].interaction_count
            
        total_sociable_procs += member.sociable_count
        total_inv_to_strangers += member.invitations_to_strangers
        total_inv_to_contacts += member.invitations_to_contacts
        total_inv_to_friends += member.invitations_to_friends
        total_succ_conn_contacts += member.successful_connections_contacts
        total_succ_conn_friends += member.successful_connections_friends
        total_succ_conn_strangers += member.successful_connections_strangers
        total_unsucc_conn_contacts += member.unsuccessful_connections_contacts
        total_unsucc_conn_friends += member.unsuccessful_connections_friends
        total_unsucc_conn_strangers += member.unsuccessful_connections_strangers
        total_met += len(member.contacts)
        total_met_through_others += member.met_through_others
        total_failed_connection_attempts += member.failed_connection_attempts
        total_successful_connection_attempts += member.successful_connection_attempts
        total_cycles_in_session += member.cycles_in_session
        total_cycles_alone += member.cycles_alone
    
    stats = list()

    avg_sessions_per_cycle = community.total_session_count/community.current_cycle
    avg_cycles_per_session = community.total_unique_session_cycles/float(community.total_unique_sessions)
    avg_members_in_session_per_cycle = community.total_members_in_session/community.current_cycle
    avg_members_per_session = avg_members_in_session_per_cycle/avg_sessions_per_cycle
    
    stats.append("\tGENERAL INFORMATION")
    stats.append("cycles: %d" % community.current_cycle)
    stats.append("members: %d" % mem_count)
    stats.append("avg. sessions per community cycle: %f" % avg_sessions_per_cycle)
    stats.append("avg. session duration: %f cycles" % avg_cycles_per_session)
    stats.append("avg. members in session per cycle: %f" % avg_members_in_session_per_cycle)
    stats.append("avg. members per session: %f" % avg_members_per_session)
    stats.append("total unique sessions: %d" % community.total_unique_sessions)
    stats.append("total unique session cycles: %d" % community.total_unique_session_cycles)
    stats.append("most popular session: %d sentibytes" % community.most_popular_session)
    stats.append("most concurrent sessions active: %d" % community.most_concurrent_sessions)
    stats.append("longest running session: %d cycles" % community.oldest_session)
    stats.append("most active members at one time: %d" % community.most_members_active)
    
    if mem_count > 0:
        avg_knowledge = total_knowledge/mem_count
        avg_false_knowledge = total_false_knowledge/mem_count
        avg_learned_from_others = total_learned_from_others/mem_count
        avg_learned_on_own = total_learned_on_own/mem_count
        avg_misled = total_misled/mem_count
        avg_corrected = total_corrected/mem_count
        avg_sociable_procs = total_sociable_procs/mem_count
        avg_cycles_in_session = total_cycles_in_session/mem_count
        avg_cycles_alone = total_cycles_alone/mem_count
        avg_inv_to_strangers = total_inv_to_strangers/mem_count
        avg_inv_to_contacts = total_inv_to_contacts/mem_count
        avg_inv_to_friends = total_inv_to_friends/mem_count
        avg_succ_conn_contacts = total_succ_conn_contacts
        avg_succ_conn_friends = total_succ_conn_friends
        avg_succ_conn_strangers = total_succ_conn_strangers
        avg_unsucc_conn_contacts = total_unsucc_conn_contacts
        avg_unsucc_conn_friends = total_unsucc_conn_friends
        avg_unsucc_conn_strangers = total_unsucc_conn_strangers
        avg_failed_connection_attempts = total_failed_connection_attempts/mem_count
        avg_successful_connection_attempts = total_successful_connection_attempts/mem_count
        avg_met = total_met/mem_count
        avg_met_through_others = total_met_through_others/mem_count
        
        avg_cycles_counted = int(avg_cycles_alone) + int(avg_cycles_in_session)
        if community.current_cycle - avg_cycles_counted > 2:
            print "sumtotal of counted cycles does not equal total cycles"
        
        stats.append("\n\tKNOWLEDGE")
        stats.append("available knowledge: %d" % len(the_truth))
        stats.append("avg. knowledge: %f" % avg_knowledge)
        stats.append("avg. false knowledge: %f" % avg_false_knowledge)
        stats.append("most knowledge: %d" % most_knowledge)
        stats.append("least knowledge: %d" % least_knowledge)
        stats.append("most accurate knowledge: %d" % most_accurate_knowledge)
        stats.append("least accurate knowledge: %d" % least_accurate_knowledge)
        stats.append("avg. learned from others: %f" % avg_learned_from_others)
        stats.append("avg. learned on own: %f" % avg_learned_on_own)
        stats.append("avg. times misled by others: %f" % avg_misled)
        stats.append("avg. times corrected by others: %f" % avg_corrected)
        
        stats.append("\n\tBEHAVIORS")
        stats.append("avg. cycles alone: %f" % avg_cycles_alone)
        stats.append("avg. cycles in session: %f" % avg_cycles_in_session)
        stats.append("avg. sociable proc count: %f" % avg_sociable_procs)
        
        stats.append("\n\tSOCIAL INTERACTION")
        stats.append("avg. failed connection attempts: %f" % avg_failed_connection_attempts)
        stats.append("avg. successful connection attempts: %f" % avg_successful_connection_attempts)
        stats.append("avg. invitations to strangers: %f" % avg_inv_to_strangers)
        stats.append("avg. invitations to contacts: %f" % avg_inv_to_contacts)
        stats.append("avg. invitations to friends: %f" % avg_inv_to_friends)
        stats.append("avg. successful connections to strangers: %f" % avg_succ_conn_strangers)
        stats.append("avg. successful connections to contacts: %f" % avg_succ_conn_contacts)
        stats.append("avg. successful connections to friends: %f" % avg_succ_conn_friends)
        stats.append("avg. unsuccessful connections to strangers: %f" % avg_unsucc_conn_strangers)
        stats.append("avg. unsuccessful connections to contacts: %f" % avg_unsucc_conn_contacts)
        stats.append("avg. unsuccessful connections to friends: %f" % avg_unsucc_conn_friends)
        stats.append("avg. others met: %f" % avg_met)
        stats.append("avg. met through others: %f" % avg_met_through_others)
    
    if contact_count > 0:
        avg_ratings = total_ratings/contact_count
        avg_avg_offset = total_avg_offset/contact_count
        avg_interactions_contacts = total_interactions_contacts/contact_count
        
        stats.append("\n\tPERCEPTIONS")
        stats.append("avg. rating: %f" % avg_ratings)
        stats.append("highest rating: %f" % highest_rating)
        stats.append("lowest rating: %f" % lowest_rating)
        stats.append("avg. perception offset: %f" % avg_avg_offset)
        stats.append("avg. interactions with contacts: %f" % avg_interactions_contacts)
    
    if friend_count > 0:
        avg_ratings_friends = total_ratings_friends/friend_count
        avg_avg_offset_friends = total_avg_offset_friends/friend_count
        avg_interactions_friends = total_interactions_friends/friend_count
        
        stats.append("\n\tFRIENDS")
        stats.append("avg. rating of friends: %f" % avg_ratings_friends)
        stats.append("avg. perception offset of friends: %f" % avg_avg_offset_friends)
        stats.append("avg. interactions with friends: %f" % avg_interactions_friends)
    
    stats.append("---------------------")
    stats.append("SENTIBYTE CONFIGURATION SETTINGS")
    
    config_lines = linesFromFile(config_file)
    
    stats += config_lines
    
    file = open(sb_summary_file, 'w')
    file = open(sb_summary_file, 'a')
    
    writeLines(stats, file)
    
    file.close()
