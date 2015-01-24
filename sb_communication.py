from random import random, randint
from sb_utilities import boundsCheck, combineAverages
from sb_fileman import readSB, writeSB

class context(object):
    def __init__(self, session, community):
        self.session = session
        self.community = community

class transmission(object):
    def __init__(self, source_ID, targets, positivity, energy, t_type, information):
        self.positivity = positivity
        self.energy = energy
        self.source_ID = source_ID
        self.targets = targets[:]
        self.t_type = t_type
        self.information = information

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
                'count': 0, 'statements': 0, 'declarations': 0,
                'avg positivity': 0, 'avg energy': 0, 
                'min positivity': 0, 'min energy': 0, 
                'max positivity': 0, 'max energy': 0}
                #'first positivity': 0, 'first energy': 0,
                #'last positivity': 0, 'last energy': 0}

    # all comparitors prioritize cycles present first, then rating
    # this way the interactions that had the most correspondance take priority
    def __eq__(self, other_interaction):
        return self.cycles_present == other_interaction.cycles_present
        
    def __ne__(self, other_interaction):
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
              
            # Interactions were once judged by the first transmission received,
            # with the intention of comparing first to last to identify mood change
            #if self.data[item]['count'] == 0:
                #self.data[item]['first positivity'] = transmission.positivity
                #self.data[item]['first energy'] = transmission.energy
            #self.data[item]['last positivity'] = transmission.positivity
            #self.data[item]['last energy'] = transmission.positivity
            
            if transmission.positivity > self.data[item]['max positivity']:
                self.data[item]['max positivity'] = transmission.positivity
            if transmission.positivity < self.data[item]['min positivity']:
                self.data[item]['min positivity'] = transmission.positivity
                
            if transmission.energy > self.data[item]['max energy']:
                self.data[item]['max energy'] = transmission.energy
            if transmission.energy < self.data[item]['min energy']:
                self.data[item]['min energy'] = transmission.energy
            
            if transmission.t_type == 'statement':
                self.data[item]['statements'] +=1
        
            if transmission.information != None:
                self.data[item]['declarations'] +=1
        
            self.data[item]['count'] += 1
            
    def guessTraits(self, cycles_present):
        self.cycles_present = cycles_present
        # The following algorithms attempt to guess the other's traits based on
        # received transmissions
        
        # COMMUNICATIVE
        # The number 12 refers to the number of communications per cycle set in
        # the session parameters
        communicative_guess = float(self.data['total']['count']) / \
                            (float(cycles_present) * 12)
        self.trait_guesses['communicative'] = boundsCheck(communicative_guess * 99)
                        
        # TALKATIVE
        if self.data['total']['count'] > 0:
            talkative_guess = float(self.data['total']['statements']) / \
                                float(self.data['total']['count']) * 99
            self.trait_guesses['talkative'] = boundsCheck(talkative_guess)
            
        # INTELLECTUAL
        if self.data['total']['statements'] > 0:
            intellectual_guess = float(self.data['total']['declarations']) / \
                                float(self.data['total']['statements']) * 99
            self.trait_guesses['intellectual'] = boundsCheck(intellectual_guess)
        
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
        # if communications per cycle changes, interaction class must be updated
        self.communications_per_cycle = 12
        self.new_members = list()
        self.community = community
        
    def __eq__(self, other):
        if other == None:
            return False
            
        else:
            return self.session_ID == other.session_ID
        
    def __ne__(self, other):
        return self.session_ID != other.session_ID
      
    def addParticipant(self, entering_ID):
        session_list_before = len(self.community.session_sb_list)
        if entering_ID in self.community.session_sb_list:
            print "attempted to add sb to multiple sessions"
            raise Exception
            
        entering = self.community.getMember(entering_ID)
        entering.joinSession(self)
        for participant_ID in self.participants:
            participant = self.community.getMember(participant_ID)
            participant.newInteraction(entering_ID)
            entering.newInteraction(participant_ID)
            
        self.community.logEntry("%s entering session %d" % (entering, self.session_ID))
        self.participants.append(entering_ID)
        self.new_members.append(entering_ID)
        self.community.session_sb_list[entering_ID] = self.session_ID
        if session_list_before == len(self.community.session_sb_list):
            print "failed to add sb to list"
            raise Exception

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
    
        self.community.logEntry("%s leaving session %d" % (leaving, self.session_ID))
        del self.community.session_sb_list[leaving_ID]
        self.community.recently_left_session.append(leaving_ID)
        leaving.leaveSession()
        self.participants.remove(leaving_ID)
        
    # Cycles through each participant, collecting broadcasts they might make
    # recieves transmission_list from cycle()
    def transmissionPhase(self, transmission_list):
        for participant_ID in self.participants:
            participant = self.community.getMember(participant_ID)
            
            if participant.proc('communicative'):
                available_targets = self.getAllOthers(participant_ID)
                if len(available_targets) > 0:
                    transmission_generated = participant.broadcast(available_targets)
                    transmission_list.append(transmission_generated)
                    
        
    # Cycles through each participant, allowing each to interpret transmissions
    # that were sent by others
    def interpretPhase(self, transmission_list):
        for participant_ID in self.participants:
            participant = self.community.getMember(participant_ID)
            for item in transmission_list:
                if participant_ID != item.source_ID:
                    participant.interpretTransmission(item)
                    
    def leavePhase(self):
        if self.current_cycle > 1:
            leaving = list()
            for participant_ID in self.participants:
                participant = self.community.getMember(participant_ID)
                if not participant.proc('stamina'):
                    leaving.append(participant_ID)
                
            for participant_ID in leaving:
                self.removeParticipant(participant_ID)
                    
            if len(self.participants) == 1:
                self.removeParticipant(self.participants[0])
                
            if len(self.participants) == 0:
                self.endPhase()
                
    # Placeholder function for any overhead work that might be involved in 
    # ending a session
    def endPhase(self):
        self.session_open = False
                
    def cycle(self):
        self.current_cycle += 1
        for member_ID in self.participants:
            member = self.community.getMember(member_ID)
            if member.current_session == None:
                print "current_session not instantiated"
                print "member.session_ID: %d" % member.current_session_ID
                raise
            self.community.logEntry("%s in session %d" % (member, self.session_ID))
            member.cycles_in_session += 1
            member.cycles_in_current_session += 1
        
        for i in range(self.communications_per_cycle):
            transmission_list = list()
            self.transmissionPhase(transmission_list)
            self.interpretPhase(transmission_list)
            
        for member_ID in self.participants:
            member = self.community.getMember(member_ID)
            if member.proc('volatility'):
                member.fluctuateTraits()
        
        if len(self.new_members) == 0:
            self.leavePhase()
        self.new_members = list()
        
        self.community.saveAndClearActiveMembers()
        
class community(object):
    def __init__(self):
        self.community_ID = randint(0, 100000)
        
        self.current_cycle = 0
        
        self.members = list()
        self.sessions = list()
        self.status_log = list()
        
        # maintains a list of sb's currently in memory
        self.active_members = list()
        self.most_members_active = 0
        self.most_concurrent_sessions = 0
        self.most_popular_session = 0
        self.oldest_session = 0
        self.total_session_count = 0
        self.total_unique_sessions = 0
        self.total_unique_session_cycles = 0
        self.total_members_in_session = 0.0
        
        self.recently_left_session = list()
        self.session_sb_list = {}
        
        # modify session limit to be part of session class, and varies depending
        # on how the session was made
        self.session_limit = 15
        
    def addMember(self, new_ID):
        self.members.append(new_ID)
        
    def logEntry(self, line):
        self.status_log.append(line)
        
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
        for member in self.active_members:
            if member.sentibyte_ID == member_ID:
                writeSB(member)
                self.active_members.remove(member)              
                return

    def saveAndClearActiveMembers(self):
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
        new_session.addParticipant(second_ID)
        self.sessions.append(new_session)
    
    def cycle(self):
        self.status_log = list()
        self.logEntry("---- cycle %d ----" % self.current_cycle)
        self.logEntry("sessions: %s" % [ID.session_ID for ID in self.sessions])
        self.total_members_in_session += len(self.session_sb_list)
        for session in self.sessions:
            self.total_session_count += 1
            if len(session.participants) > self.most_popular_session:
                self.most_popular_session = len(session.participants)
            if session.current_cycle > self.oldest_session:
                self.oldest_session = session.current_cycle
            session.cycle()
            
        void_sessions = [session for session in self.sessions if session.session_open == False]
        
        for session in void_sessions:
            self.total_unique_sessions += 1
            self.total_unique_session_cycles += session.current_cycle
            self.sessions.remove(session)
        
        members_alone = [ID for ID in self.members if self.getAvailability(ID) == 'alone']
        self.logEntry("members alone: %d" % len(members_alone))
        self.logEntry("members recently left session: %d" % len(self.recently_left_session))
        self.logEntry("members in session: %d" % len(self.session_sb_list))
        for member_ID in members_alone:
            member = self.getMember(member_ID) 
            self.logEntry("%s is alone" % member_ID)
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
        
        return self.status_log
