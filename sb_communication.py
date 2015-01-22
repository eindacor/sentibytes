from random import random, randint
from sb_utilities import boundsCheck, weightedAverage
from sb_fileman import readSB, writeSB

class transmission(object):
    def __init__(self, source_ID, targets, positivity, energy, t_type, information):
        self.positivity = positivity
        self.energy = energy
        self.source_ID = source_ID
        self.targets = targets[:]
        self.t_type = t_type
        self.information = information

class interaction(object):
    def __init__(self, owner_ID, other_ID, session):
        self.session = session
        self.first_cycle = self.session.current_cycle
        self.owner_ID = owner_ID
        self.other_ID = other_ID
        self.others_present = list()
        self.overall_rating = None
        
        owner = readSB(owner_ID)
        if other_ID not in owner.perceptions:
            self.overall_rating = owner['regard']['current']
            
        else:
            self.overall_rating = owner.getRating(other_ID)

        writeSB(owner)
        
        self.g_traits = {}
        self.cycles_present = 0
        
        recorded_data = ('owner', 'others', 'total')
        
        self.data = {}
        for item in recorded_data:
            self.data[item] = {
                'count': 0, 'statements': 0, 'declarations': 0,
                'avg positivity': 0, 'avg energy': 0, 
                'min positivity': 0, 'min energy': 0, 
                'max positivity': 0, 'max energy': 0,
                'first positivity': 0, 'first energy': 0,
                'last positivity': 0, 'last energy': 0}

    def __eq__(self, other_ID):
        other = readSB(other_ID)
        if self.cycles_present < 4:
            return self.cycles_present == other.cycles_present
        else:
            return self.overall_rating == other.overall_rating
        
    def __ne__(self, other_ID):
        other = readSB(other_ID)
        if self.cycles_present < 4:
            return self.cycles_present != other.cycles_present
        else:
            return self.overall_rating != other.overall_rating
        
    def __gt__(self, other_ID):
        other = readSB(other_ID)
        if self.cycles_present < 4:
            return self.cycles_present > other.cycles_present
        else:
            return self.overall_rating > other.overall_rating
        
    def __ge__(self, other_ID):
        other = readSB(other_ID)
        if self.cycles_present < 4:
            return self.cycles_present >= other.cycles_present
        else:
            return self.overall_rating >= other.overall_rating
        
    def __lt__(self, other_ID):
        other = readSB(other_ID)
        if self.cycles_present < 4:
            return self.cycles_present < other.cycles_present
        else:
            return self.overall_rating < other.overall_rating
        
    def __le__(self, other_ID):
        other = readSB(other_ID)
        if self.cycles_present < 4:
            return self.cycles_present <= other.cycles_present
        else:
            return self.overall_rating <= other.overall_rating
        
    def __getitem__(self, index):
        return self.data[index]
        
    def addTransmission(self, transmission):
        # adjust stamina levels based on mood, stay longer for good results
        self.others_present = [target for target in transmission.targets if target != self.owner_ID]
            
        audience = ['total'] 
            
        if not self.owner_ID in transmission.targets:
            audience.append('others')
            
        elif len(transmission.targets) == 1:
            audience.append('owner')
            
        for item in audience:
            self.data[item]['avg positivity'] = \
                weightedAverage(self.data[item]['avg positivity'],
                self.data[item]['count'], transmission.positivity, 1)
                
            self.data[item]['avg energy'] = \
                weightedAverage(self.data[item]['avg energy'],
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
            
            self.updateInteraction()
            
    def updateInteraction(self):
        owner = readSB(self.owner_ID)
        self.cycles_present = 1 + (owner.getSession().current_cycle - self.first_cycle)
            
        # The following algorithms attempt to guess the other's traits based on
        # received transmissions
        # COMMUNICATIVE
        communicative_guess = float(self.data['total']['count']) / \
                            (float(self.cycles_present) * self.session.communications_per_cycle)
        self.g_traits['communicative'] = communicative_guess * 99
                        
        # TALKATIVE
        if self.data['total']['count'] > 0:
            talkative_guess = float(self.data['total']['statements']) / \
                                float(self.data['total']['count']) * 99
            self.g_traits['talkative'] = talkative_guess
            
        # INTELLECTUAL
        if self.data['total']['statements'] > 0:
            intellectual_guess = float(self.data['total']['declarations']) / \
                                float(self.data['total']['statements']) * 99
            self.g_traits['intellectual'] = intellectual_guess
        
        # POSITIVITY
        self.g_traits['positivity'] = float(self.data['total']['avg positivity'])

        # ENERGY     
        self.g_traits['energy'] = float(self.data['total']['avg energy'])
        
        ratings = list()
        for key in self.g_traits:
            acceptable_range = owner.d_traits[key]['upper'] - owner.d_traits[key]['lower']
            delta = abs(owner.getDesired(key) - self.g_traits[key])
            rating = acceptable_range - float(delta)
            rating = boundsCheck(rating)
            priority = owner.desire_priority[key]
            for i in range(priority):
                ratings.append(rating)
        
        self.overall_rating = float(sum(ratings)) / float(len(ratings))
        
        writeSB(owner)
    
        return self.overall_rating

# This is the managing class for social interactions between sentibytes.
# Sentibytes involved in a session are called 'participants'
class session(object):
    def __init__(self, community):
        self.session_ID = randint(0, 10000)
        self.participants = list()
        self.current_cycle = 0
        self.session_open = True
        self.communications_per_cycle = 12
        self.new_members = list()
        self.community = community
        
    def __str__(self):
        return str(self.session_ID)
        
    def __eq__(self, other):
        if other == None:
            return False
            
        else:
            return self.session_ID == other.session_ID
        
    def __ne__(self, other):
        return self.session_ID != other.session_ID
        
    def addParticipant(self, entering_ID):
        entering = readSB(entering_ID)
        entering.current_session = self
        for sb_ID in self.participants:
            sb = readSB(sb_ID)
            sb.addInteraction(entering_ID)
            entering.addInteraction(sb_ID)
            writeSB(sb)
            
        self.community.logEntry("%s entering session %d" % (entering, self.session_ID))
        self.participants.append(entering_ID)
        self.new_members.append(entering_ID)
        writeSB(entering)
        
    def getAllOthers(self, participant_ID):
        other_participants = [p_ID for p_ID in self.participants if p_ID != participant_ID]
        return other_participants
    
    def removeParticipant(self, leaving_ID):
        leaving = readSB(leaving_ID)
        other_participants = self.getAllOthers(leaving.sentibyte_ID)
        for participant_ID in other_participants:
            participant = readSB(participant_ID)
            leaving.endInteraction(participant)
            participant.endInteraction(leaving)
            writeSB(participant)
    
        self.community.logEntry("%s leaving session %d" % (leaving, self.session_ID))
        leaving.removeSession()
        self.participants.remove(leaving)
        writeSB(leaving)
        
    # Cycles through each participant, collecting broadcasts they might make
    # recieves transmission_list from cycle()
    def transmissionPhase(self, transmission_list):
        for participant_ID in self.participants:
            participant = readSB(participant_ID)
            
            if participant.proc('communicative'):
                available_targets = self.getAllOthers(participant)
                if len(available_targets) > 0:
                    transmission_list.append(participant.broadcast(available_targets))
                    
            writeSB(participant)
        
    # Cycles through each participant, allowing each to interpret transmissions
    # that were sent by others
    def interpretPhase(self, transmission_list):
        for participant_ID in self.participants:
            participant = readSB(participant_ID)
            for item in transmission_list:
                if participant != item.source_ID:
                    participant.interpretTransmission(item)
                    
            writeSB(participant)
                    
    def leavePhase(self):   
        leaving = list()
        for participant_ID in self.participants:
            participant = readSB(participant_ID)
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
        for member_ID in self.participants:
            member = readSB(member_ID)
            self.community.logEntry("%s in session %d" % (member, self.session_ID))
            member.cycles_in_session += 1
            writeSB(member)
        
        for i in range(self.communications_per_cycle):
            transmission_list = list()
            self.transmissionPhase(transmission_list)
            self.interpretPhase(transmission_list)
            
        for member_ID in self.participants:
            member = readSB(member_ID)
            if member.proc('volatility'):
                member.fluctuateTraits()
            writeSB(member)
        
        self.current_cycle += 1
        if len(self.new_members) == 0:
            self.leavePhase()
        self.new_members = list()
        
class community(object):
    def __init__(self):
        self.community_ID = randint(0, 100000)
        
        self.current_cycle = 0
        
        self.members = list()
        self.sessions = list()
        self.status_log = list()
        
    def addMember(self, new_ID):
        self.members.append(new_ID)
        new = readSB(new_ID)
        new.addCommunity(self)
        writeSB(new)
        
    def logEntry(self, line):
        self.status_log.append(line)
        
    def getAllOthers(self, member_ID):
        other_members = self.members[:]
        other_members.remove(member_ID)
        return other_members
        
    def createSession(self, first_ID, second_ID):
        new_session = session(self)
        new_session.addParticipant(first_ID)
        new_session.addParticipant(second_ID)
        self.sessions.append(new_session)
        
    def cycle(self):
        self.status_log = list()
        self.logEntry("---- cycle %d ----" % self.current_cycle)
        self.logEntry("sessions: %s" % [ID.session_ID for ID in self.sessions])
        for session in self.sessions:
            session.cycle()
            
        void_sessions = [session for session in self.sessions if session.session_open == False]
        
        for session in void_sessions:
            self.sessions.remove(session)
         
        members_alone = list()
        for member_ID in self.members:
            member = readSB(member_ID) 
            if member.isAvailable():
                members_alone.append(member_ID)
                
        
        self.logEntry("members alone: %d" % len(members_alone))
        for member_ID in members_alone:
            member = readSB(member_ID) 
            self.logEntry("%s is alone" % member_ID)
            member.aloneCycle()
            writeSB(member)
                
        for member_ID in self.members:
            member = readSB(member_ID) 
            if member.isAvailable():
                member.invitationCycle()
            writeSB(member)
                
        self.current_cycle += 1
        
        return self.status_log
