from sb_fileman import linesFromFile, readSB, writeSB
from sb_utilities import averageContainer

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
                
    writeLines(member_info, file)
    file.close()
    
def updateStatusLog(sb_status_file, status_log_lines, overwrite=True):
    if overwrite:
        file = open(sb_status_file, 'w')
        
    file = open(sb_status_file, 'a')
                
    writeLines(status_log_lines, file)
    file.close()

def updateSummary(community, config_file, sb_summary_file, the_truth):
    most_accurate_knowledge = 0
    least_accurate_knowledge = len(the_truth)
    most_knowledge = 0
    least_knowledge = len(the_truth)
    most_false_knowledge = 0
    least_false_knowledge = len(the_truth)
    highest_rating = 0
    lowest_rating = 100
    oldest_sb = 0
    
    avg_rating = averageContainer()
    avg_rating_friends = averageContainer()
    avg_rating_non_friends = averageContainer()
    avg_rating_best_friend = averageContainer()
    avg_lowest_rating = averageContainer()
    avg_desired_offset = averageContainer()
    avg_desired_offset_friends = averageContainer()
    avg_desired_offset_non_friends = averageContainer()
    avg_knowledge = averageContainer()
    avg_accurate_knowledge = averageContainer()
    avg_false_knowledge = averageContainer()
    avg_learned_from_others = averageContainer()
    avg_learned_on_own = averageContainer()
    avg_misled = averageContainer()
    avg_corrected = averageContainer()
    avg_cycles_in_session = averageContainer()
    avg_cycles_alone = averageContainer()
    avg_inv_to_strangers = averageContainer()
    avg_inv_to_contacts = averageContainer()
    avg_inv_to_friends = averageContainer()
    avg_succ_conn_contacts = averageContainer()
    avg_succ_conn_friends = averageContainer()
    avg_succ_conn_strangers = averageContainer()
    avg_unsucc_conn_contacts = averageContainer()
    avg_unsucc_conn_friends = averageContainer()
    avg_unsucc_conn_strangers = averageContainer()
    avg_rejections = averageContainer()
    avg_accepts = averageContainer()
    avg_failed_connection_attempts = averageContainer()
    avg_successful_connection_attempts = averageContainer()
    avg_met = averageContainer()
    avg_met_through_others = averageContainer()
    avg_met_on_own = averageContainer()
    avg_interactions = averageContainer()
    avg_interactions_friends = averageContainer()
    avg_interactions_non_friends = averageContainer()
    avg_interaction_rating = averageContainer()
    avg_rumors_per_perception = averageContainer()
    avg_memories_per_perception = averageContainer()
    avg_children = averageContainer()
    avg_family_size = averageContainer()
    avg_bonds_denied = averageContainer()
    avg_bonds_postponed = averageContainer()
    avg_bonds_found = averageContainer()
    avg_bonds = averageContainer()
    avg_age = averageContainer()
    
    mem_count = float(len(community.members))
    for member_ID in community.members:
        member = readSB(member_ID)
        member_total_knowledge = len(member.accurate_knowledge) + len(member.false_knowledge)
        if member_total_knowledge > most_knowledge:
            most_knowledge = member_total_knowledge
        if member_total_knowledge < least_knowledge:
            least_knowledge = member_total_knowledge
        if len(member.accurate_knowledge) > most_accurate_knowledge:
            most_accurate_knowledge = len(member.accurate_knowledge)
        if len(member.accurate_knowledge) < least_accurate_knowledge:
            least_accurate_knowledge = len(member.accurate_knowledge)
        if len(member.false_knowledge) > most_false_knowledge:
            most_false_knowledge = len(member.false_knowledge)
        if len(member.false_knowledge) < least_false_knowledge:
            least_false_knowledge = len(member.false_knowledge)
        if member.age > oldest_sb:
            oldest_sb = member.age
            
        avg_knowledge.addValue(member_total_knowledge)
        avg_accurate_knowledge.addValue(len(member.accurate_knowledge))
        avg_false_knowledge.addValue(len(member.false_knowledge))
        avg_misled.addValue(member.misled_by_others)
        avg_corrected.addValue(member.corrected_by_others)
        avg_learned_from_others.addValue(member.learned_from_others)
        avg_learned_on_own.addValue(member.learned_on_own)
        
        lowest_other_rating = 100.0
        best_friend_rating = 0.0
        for other_ID in member.contacts:
            other_rating = member.getRating(other_ID)
            avg_rating.addValue(other_rating)
            if other_rating > highest_rating:
                highest_rating = other_rating
            elif other_rating < lowest_rating:
                lowest_rating = other_rating
            if other_rating < lowest_other_rating:
                lowest_other_rating = other_rating
            other_perception = member.perceptions[other_ID]
            other_interaction_count = other_perception.avg_interaction_rating.count
            other_interaction_rating = other_perception.avg_interaction_rating.average
            avg_interactions.addValue(other_interaction_count)
            avg_interaction_rating.addValue(other_interaction_rating)
            other_desired_offset = other_perception.avg_desired_offset.average
            avg_desired_offset.addValue(other_desired_offset)
            avg_rumors_per_perception.addValue(other_perception.rumors_heard)
            avg_memories_per_perception.addValue(other_perception.memories_counted)

            if other_ID in member.friend_list:
                if other_rating > best_friend_rating:
                    best_friend_rating = other_rating
                avg_rating_friends.addValue(other_rating)
                avg_desired_offset_friends.addValue(other_desired_offset)
                avg_interactions_friends.addValue(other_interaction_count)
                
            else:
                avg_rating_non_friends.addValue(other_rating)
                avg_desired_offset_non_friends.addValue(other_desired_offset)
                avg_interactions_non_friends.addValue(other_interaction_count)
        if best_friend_rating > 1:
            avg_rating_best_friend.addValue(best_friend_rating)
        if lowest_other_rating < 100.0:
            avg_lowest_rating.addValue(lowest_other_rating)
            
        avg_children.addValue(len(member.children))
        avg_family_size.addValue(len(member.family))
        avg_inv_to_strangers.addValue(member.invitations_to_strangers)
        avg_inv_to_contacts.addValue(member.invitations_to_contacts)
        avg_inv_to_friends.addValue(member.invitations_to_friends)
        avg_succ_conn_contacts.addValue(member.successful_connections_contacts)
        avg_succ_conn_friends.addValue(member.successful_connections_friends)
        avg_succ_conn_strangers.addValue(member.successful_connections_strangers)
        avg_unsucc_conn_contacts.addValue(member.unsuccessful_connections_contacts)
        avg_unsucc_conn_friends.addValue(member.unsuccessful_connections_friends)
        avg_unsucc_conn_strangers.addValue(member.unsuccessful_connections_strangers)
        avg_rejections.addValue(member.rejection_count)
        avg_accepts.addValue(member.accepted_count)
        avg_met.addValue(len(member.contacts))
        avg_met_through_others.addValue(member.met_through_others)
        avg_met_on_own.addValue(member.met_on_own)
        avg_failed_connection_attempts.addValue(member.failed_connection_attempts)
        avg_successful_connection_attempts.addValue(member.successful_connection_attempts)
        avg_cycles_in_session.addValue(member.cycles_in_session)
        avg_cycles_alone.addValue(member.cycles_alone)
        avg_bonds_denied.addValue(member.bonds_denied)
        avg_bonds_found.addValue(member.bonds_confirmed)
        avg_bonds_postponed.addValue(member.bonds_postponed)
        avg_bonds.addValue(len(member.bonds))
        avg_age.addValue(member.age)
        
    stats = list()
    
    stats.append("\tGENERAL INFORMATION")
    stats.append("cycles: %d" % community.current_cycle)
    stats.append("avg. seconds per cycle: %f" % community.seconds_per_cycle.average)
    stats.append("members: %d" % mem_count)
    stats.append("children created: %d" % community.children_born)
    stats.append("members deceased: %d" % community.deceased_members)
    stats.append("avg. sessions per community cycle: %s" % community.sessions_per_cycle)
    stats.append("avg. session duration: %s cycles" % community.cycles_per_session)
    stats.append("avg. members in session per cycle: %s" % community.members_in_session)
    stats.append("avg. members per session: %s" % community.members_per_session)
    stats.append("avg. participant limit: %s" % community.avg_participant_limit)
    stats.append("total unique sessions: %d" % community.cycles_per_session.count)
    stats.append("most popular session: %d sentibytes" % community.most_popular_session)
    stats.append("most concurrent sessions active: %d" % community.most_concurrent_sessions)
    stats.append("longest running session: %d cycles" % community.oldest_session)
    stats.append("most active members at one time: %d" % community.most_members_active)
    stats.append("average age: %s" % avg_age)
    stats.append("oldest member: %d" % oldest_sb)
    stats.append("avg. age of death: %s" % community.avg_age_of_death)
    
    stats.append("\n\tKNOWLEDGE")
    stats.append("available knowledge: %s" % len(the_truth))
    stats.append("avg. knowledge: %s" % avg_knowledge)
    stats.append("avg. accurate knowledge: %s" % avg_accurate_knowledge)
    stats.append("avg. false knowledge: %s" % avg_false_knowledge)
    stats.append("most knowledge: %d" % most_knowledge)
    stats.append("least knowledge: %d" % least_knowledge)
    stats.append("most accurate knowledge: %d" % most_accurate_knowledge)
    stats.append("least accurate knowledge: %d" % least_accurate_knowledge)
    stats.append("most false knowledge: %d" % most_false_knowledge)
    stats.append("least false knowledge: %d" % least_false_knowledge)
    stats.append("avg. learned from others: %s" % avg_learned_from_others)
    stats.append("avg. learned on own: %s" % avg_learned_on_own)
    stats.append("avg. times misled by others: %s" % avg_misled)
    stats.append("avg. times corrected by others: %s" % avg_corrected)
    
    stats.append("\n\tBEHAVIORS")
    stats.append("avg. cycles alone: %s" % avg_cycles_alone)
    stats.append("avg. cycles in session: %s" % avg_cycles_in_session)
    stats.append("avg. number of children: %s" % avg_children)
    stats.append("avg. family size: %s" % avg_family_size)
    stats.append("avg. potential bonds: %s" % avg_bonds)
    stats.append("avg. bonds denied: %s" % avg_bonds_denied)
    stats.append("avg. bonds postponed: %s" % avg_bonds_postponed)
    stats.append("avg. bonds confirmed: %s" % avg_bonds_found)
    
    stats.append("\n\tSOCIAL INTERACTION")
    stats.append("avg. failed connection attempts: %s" % avg_failed_connection_attempts)
    stats.append("avg. successful connection attempts: %s" % avg_successful_connection_attempts)
    stats.append("avg. invitations to strangers: %s" % avg_inv_to_strangers)
    stats.append("avg. invitations to contacts: %s" % avg_inv_to_contacts)
    stats.append("avg. invitations to friends: %s" % avg_inv_to_friends)
    stats.append("avg. successful connections to strangers: %s" % avg_succ_conn_strangers)
    stats.append("avg. successful connections to contacts: %s" % avg_succ_conn_contacts)
    stats.append("avg. successful connections to friends: %s" % avg_succ_conn_friends)
    stats.append("avg. unsuccessful connections to strangers: %s" % avg_unsucc_conn_strangers)
    stats.append("avg. unsuccessful connections to contacts: %s" % avg_unsucc_conn_contacts)
    stats.append("avg. unsuccessful connections to friends: %s" % avg_unsucc_conn_friends)
    stats.append("avg. times not wanted contact: %s" % avg_rejections)
    stats.append("avg. times wanted contact: %s" % avg_accepts)
    stats.append("avg. others met: %s" % avg_met)
    stats.append("avg. met through others: %s" % avg_met_through_others)
    stats.append("avg. met on own: %s" % avg_met_on_own)
    

    stats.append("\n\tPERCEPTIONS")
    stats.append("highest rating: %f" % highest_rating)
    stats.append("lowest rating: %f" % lowest_rating)
    stats.append("avg. rating: %s" % avg_rating)
    stats.append("avg. best friend rating: %s" % avg_rating_best_friend)
    stats.append("avg. lowest rating: %s" % avg_lowest_rating)
    stats.append("avg. friend rating: %s" % avg_rating_friends)
    stats.append("avg. non-friend rating: %s" % avg_rating_non_friends)
    stats.append("avg. desired offset: %s" % avg_desired_offset)
    stats.append("avg. friend desired offset: %s" % avg_desired_offset_friends)
    stats.append("avg. non-friend desired offset: %s" % avg_desired_offset_non_friends)
    stats.append("avg. interactions with others: %f" % avg_interactions)
    stats.append("avg. interactions with friends: %f" % avg_interactions_friends)
    stats.append("avg. interactions with non-friends: %f" % avg_interactions_non_friends)
    stats.append("avg. rumors heard per perception: %s" % avg_rumors_per_perception)
    stats.append("avg. memories relived per perception: %s" % avg_memories_per_perception)
    
    stats.append("---------------------")
    stats.append("SENTIBYTE CONFIGURATION SETTINGS")
    
    config_lines = linesFromFile(config_file)
    
    stats += config_lines
    
    file = open(sb_summary_file, 'w')
    file = open(sb_summary_file, 'a')
    
    writeLines(stats, file)
    
    file.close()
