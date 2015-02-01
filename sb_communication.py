from random import random, randint
from sb_utilities import boundsCheck, combineAverages, averageContainer
from sb_fileman import readSB, writeSB
from datetime import datetime

class context(object):
    def __init__(self, session, community):
        self.session = session
        self.community = community

class transmission(object):
    def __init__(self, source_ID, targets, positivity, energy, t_type, knowledge=None, gossip=None, brag=None):
        self.positivity = positivity
        self.energy = energy
        self.source_ID = source_ID
        self.targets = targets[:]
        self.t_type = t_type
        self.knowledge = knowledge
        self.gossip = gossip
        self.brag = brag

class interaction(object):
    def __init__(self, owner_ID, other_ID):
        self.owner_ID = owner_ID
        self.other_ID = other_ID
        
        self.trait_guesses = {}
        self.cycles_present = 0
        
        recorded_data = ('owner', 'others', 'total')
        
        self.data = {}
        for item in recorded_data:
            self.data[item] = {
                'count': 0, 'statements': 0, 'knowledge': 0,
                'gossip': 0, 'brag': 0,
                'avg positivity': 0, 'avg energy': 0}

    # all comparitors prioritize cycles present first, then rating
    # this way the interactions that had the most correspondance take priority
    def __eq__(self, other_interaction):
        if other_interaction == None:
            return False
        else:
            return self.cycles_present == other_interaction.cycles_present
        
    def __ne__(self, other_interaction):
        if other_interaction == None:
            return True
        else:
            return self.cycles_present != other_interaction.cycles_present
        
    def __gt__(self, other_interaction):
        return self.cycles_present > other_interaction.cycles_present
        
    def __ge__(self, other_interaction):
        return self.cycles_present >= other_interaction.cycles_present
        
    def __lt__(self, other_interaction):
        return self.cycles_present < other_interaction.cycles_present

    def __le__(self, other_interaction):
        return self.cycles_present <= other_interaction.cycles_present
        
    def __getitem__(self, index):
        return self.data[index]
        
    def addTransmission(self, transmission):
        # this list made to differentiate messages to the owner, to others, or both   
        audience = ['total'] 
            
        if self.owner_ID not in transmission.targets:
            audience.append('others')
            
        elif len(transmission.targets) == 1:
            audience.append('owner')
            
        for item in audience:
            self.data[item]['avg positivity'] = \
                combineAverages(self.data[item]['avg positivity'],
                self.data[item]['count'], transmission.positivity, 1)
                
            self.data[item]['avg energy'] = \
                combineAverages(self.data[item]['avg energy'],
                self.data[item]['count'], transmission.energy, 1)
            
            '''
            if transmission.positivity > self.data[item]['max positivity']:
                self.data[item]['max positivity'] = transmission.positivity
            if transmission.positivity < self.data[item]['min positivity']:
                self.data[item]['min positivity'] = transmission.positivity
                
            if transmission.energy > self.data[item]['max energy']:
                self.data[item]['max energy'] = transmission.energy
            if transmission.energy < self.data[item]['min energy']:
                self.data[item]['min energy'] = transmission.energy
            '''
            
            if transmission.t_type == 'statement':
                self.data[item]['statements'] +=1
        
            if transmission.knowledge != None :
                self.data[item]['knowledge'] +=1
                
            if transmission.gossip != None :
                self.data[item]['gossip'] +=1
                
            if transmission.brag != None :
                self.data[item]['brag'] +=1
        
            self.data[item]['count'] += 1
            
    def guessTraits(self, cycles_present, communications_per_cycle):
        self.cycles_present = cycles_present
        # The following algorithms attempt to guess the other's traits based on
        # received transmissions
        
        # COMMUNICATIVE
        communicative_guess = float(self.data['total']['count']) / \
                            (float(cycles_present) * communications_per_cycle)
        self.trait_guesses['communicative'] = boundsCheck(communicative_guess * 100)
                        
        # TALKATIVE
        if self.data['total']['count'] > 0:
            talkative_guess = float(self.data['total']['statements']) / \
                                float(self.data['total']['count']) * 100
            self.trait_guesses['talkative'] = boundsCheck(talkative_guess)
            
        # INTELLECTUAL
        if self.data['total']['statements'] > 0:
            intellectual_guess = float(self.data['total']['knowledge']) / \
                                float(self.data['total']['statements']) * 100
            self.trait_guesses['intellectual'] = boundsCheck(intellectual_guess)
            
        # GOSSIPY
        if self.data['total']['statements'] > 0:
            gossipy_guess = float(self.data['total']['gossip']) / \
                                float(self.data['total']['statements']) * 100
            self.trait_guesses['gossipy'] = boundsCheck(gossipy_guess)
            
        # CONFIDENT
        if self.data['total']['statements'] > 0:
            confident_guess = float(self.data['total']['brag']) / \
                                float(self.data['total']['statements']) * 100
            self.trait_guesses['confident'] = boundsCheck(confident_guess)
        
        # POSITIVITY
        self.trait_guesses['positivity'] = float(self.data['total']['avg positivity'])

        # ENERGY     
        self.trait_guesses['energy'] = float(self.data['total']['avg energy'])

# This is the managing class for social interactions between sentibytes.
# Sentibytes involved in a session are called 'participants'
class session(object):
    def __init__(self, community, ID):
        self.session_ID = ID
        self.participants = list()
        self.current_cycle = 0
        self.session_open = True
        self.new_members = list()
        self.community = community
        self.session_active = False
        self.leaving_list = list()
        
    def __eq__(self, other):
        if other == None:
            return False
        else:
            return self.session_ID == other.session_ID
        
    def __ne__(self, other):
        if other == None:
            return True
        else:
            return self.session_ID != other.session_ID
      
    def addParticipant(self, entering_ID, inviter_ID=None):
        entering = self.community.getMember(entering_ID)
        entering.joinSession(self)
        for participant_ID in self.participants:
            participant = self.community.getMember(participant_ID)
            
            # following code monitors how sb's meet others, either by direct 
            # connection or by meeting through another sb
            if entering_ID not in participant.contacts:
                if participant_ID == inviter_ID:
                    participant.met_on_own += 1
                    entering.met_on_own += 1
                
                else:
                    participant.met_through_others += 1
                    entering.met_through_others += 1
            
            participant.newInteraction(entering_ID)
            entering.newInteraction(participant_ID)
            
            if not self.session_active:
                self.community.deactivateMember(participant_ID)
            
        self.participants.append(entering_ID)
        self.new_members.append(entering_ID)
        self.community.session_sb_list[entering_ID] = self.session_ID
        
        if not self.session_active:
            self.community.deactivateMember(entering_ID)

    def getAllOthers(self, participant_ID):
        other_participants = [p_ID for p_ID in self.participants if p_ID != participant_ID]
        return other_participants
    
    def removeParticipant(self, leaving_ID):
        leaving = self.community.getMember(leaving_ID)
        other_participants = self.getAllOthers(leaving.sentibyte_ID)
        for participant_ID in other_participants:
            participant = self.community.getMember(participant_ID)
            leaving.endInteraction(participant_ID)
            participant.endInteraction(leaving_ID)
    
        del self.community.session_sb_list[leaving_ID]
        self.community.recently_left_session.append(leaving_ID)
        leaving.leaveSession()
        self.participants.remove(leaving_ID)
    
    def distributeTransmissions(self, source_ID, transmission_list):
        audience = self.getAllOthers(source_ID)
        for other_ID in audience:
            other = self.community.getMember(other_ID)
            for transmission in transmission_list:
                other.interpretTransmission(transmission)
    
    def sessionCleanup(self):
        for other_ID in self.leaving_list:
            if other_ID in self.participants:
                self.removeParticipant(other_ID)
            
        if len(self.participants) < 2:
            for other_ID in self.participants:
                self.removeParticipant(other_ID)
            self.session_open = False
            
        self.new_members = list()
        self.leaving_list = list()
        self.community.saveAndClearActiveMembers()
                
    def cycle(self):
        self.current_cycle += 1
        
        for sb_ID in self.participants:
            sb = self.community.getMember(sb_ID)
            sb.sessionCycle()
            
        self.sessionCleanup()
        
class community(object):
    def __init__(self, keep_members_active=False):
        self.community_ID = randint(0, 100000)
        
        self.current_cycle = 0
        
        self.members = list()
        self.children = list()
        self.max_children = list()
        self.sessions = list()
        self.status_log = list()
        
        # maintains a list of sb's currently in memory
        self.active_members = list()
        self.most_members_active = 0
        self.most_concurrent_sessions = 0
        self.most_popular_session = 0
        self.oldest_session = 0
        self.sessions_per_cycle = averageContainer()
        self.cycles_per_session = averageContainer()
        self.members_in_session = averageContainer()
        self.members_per_session = averageContainer()
        self.avg_age_of_death = averageContainer()
        self.deceased_members = 0
        
        self.recently_left_session = list()
        self.session_sb_list = {}
        self.communications_per_cycle = 20
        self.children_born = 0
        self.child_age = 20
        self.child_limit = 3
        
        self.seconds_per_cycle = averageContainer()
        
        # modify session limit to be part of session class, and varies depending
        # on how the session was made
        self.session_limit = 15
        
        # when True, members stay in memory instead of relying on file access
        self.keep_members_active = keep_members_active
        
    def removeMember(self, other_ID):
        other = self.getMember(other_ID)
        self.avg_age_of_death.addValue(other.age)
        if other_ID in self.session_sb_list:
            # add trauma for all other members in session
            session = self.getSession(other.current_session_ID)
            already_active = session.session_active
            session.session_active = True
            session.removeParticipant(other_ID)
            session.sessionCleanup()
            session.session_active = already_active
            
        self.deactivateMember(other_ID)
            
        if other_ID in self.children:
            self.children.remove(other_ID)
        if other_ID in self.max_children:
            self.max_children.remove(other_ID)
        self.members.remove(other_ID)
        self.deceased_members += 1
        
    def addMember(self, new_ID):
        self.members.append(new_ID)
        self.children.append(new_ID)
        
    def getSession(self, session_ID):
        # porobably an easier way to do this
        for session in self.sessions:
            if session_ID == session.session_ID:
                return session
    
    def getAvailability(self, member_ID):
        if member_ID in self.recently_left_session:
            return 'recently left'
        
        if member_ID in self.session_sb_list:
            session_ID = self.session_sb_list[member_ID]
            session = self.getSession(session_ID)
            if len(session.participants) >= self.session_limit:
                return 'in full session'
                
            else:
                return 'in open session'
                
        else:
            return 'alone'
    
    # returns member in active_member list, activates member if they are not
    # in the list
    def getMember(self, member_ID):
        active_IDs = [member.sentibyte_ID for member in self.active_members]
        if member_ID not in active_IDs:
            self.active_members.append(readSB(member_ID, self))
           
        if len(self.active_members) > self.most_members_active:
            self.most_members_active = len(self.active_members)
            
        for member in self.active_members:
            if member_ID == str(member):
                return member

    # removes sb from memory, saving to file
    def deactivateMember(self, member_ID):
        if not self.keep_members_active:
            for member in self.active_members:
                if member.sentibyte_ID == member_ID:
                    writeSB(member)
                    self.active_members.remove(member)              
                    return

    def saveAndClearActiveMembers(self):
        if not self.keep_members_active:
            if len(self.active_members) > self.most_members_active:
                self.most_members_active = len(self.active_members)
            for member in self.active_members:
                writeSB(member)
            
            self.active_members = list()
        
    def getAllOthers(self, member_ID):
        other_members = self.members[:]
        other_members.remove(member_ID)
        return other_members
        
    def createSession(self, first_ID, second_ID):
        unavailable_IDs = [s.session_ID for s in self.sessions]
        new_ID = 1
        while new_ID in unavailable_IDs:
            new_ID += 1
            
        new_session = session(self, new_ID)
        new_session.addParticipant(first_ID)
        new_session.addParticipant(second_ID, inviter_ID=first_ID)
        self.sessions.append(new_session)
    
    def cycle(self):
        cycle_start = datetime.now()
        self.members_in_session.addValue(len(self.session_sb_list))
        self.sessions_per_cycle.addValue(len(self.sessions))
        
        for session in self.sessions:
            session.session_active = True
            self.members_per_session.addValue(len(session.participants))
            if len(session.participants) > self.most_popular_session:
                self.most_popular_session = len(session.participants)
            if session.current_cycle > self.oldest_session:
                self.oldest_session = session.current_cycle
            session.cycle()
            session.session_active = False
            
        void_sessions = [session for session in self.sessions if session.session_open == False]
        
        for session in void_sessions:
            self.cycles_per_session.addValue(session.current_cycle)
            self.sessions.remove(session)
        
        members_alone = [ID for ID in self.members if self.getAvailability(ID) == 'alone']
        for member_ID in members_alone:
            member = self.getMember(member_ID) 
            member.aloneCycle()
            self.deactivateMember(member_ID)
        
        members_inviting = [ID for ID in self.members if self.getAvailability(ID) == 'in open session' \
                            or self.getAvailability(ID) == 'alone']   
        for member_ID in members_inviting:
            member = self.getMember(member_ID) 
            member.invitationCycle()
            self.deactivateMember(member_ID)
                
        self.current_cycle += 1
        
        self.saveAndClearActiveMembers()

        if len(self.sessions) > self.most_concurrent_sessions:
            self.most_concurrent_sessions = len(self.sessions)
        
        self.recently_left_session = list()
        cycle_end = datetime.now()
        time_spent = cycle_end - cycle_start
        actual_time = float(time_spent.seconds) + (time_spent.microseconds/float(1000000))
        self.seconds_per_cycle.addValue(actual_time)
        print "cycle duration: %f" % actual_time
        print "average seconds per cycle: %f" % self.seconds_per_cycle
        print "-----"
        
        return self.status_log
