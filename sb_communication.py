from random import random, randint
from sb_utilities import newAverage

class transmission(object):
    def __init__(self, source, targets, positivity, energy, t_type):
        self.positivity = positivity
        self.energy = energy
        self.source = source
        self.targets = list()
        self.targets.append(targets)
        self.t_type = t_type
        
    def printStats(self):
        print "TESTING"

class interaction(object):
    def __init__(self, owner, other):
        self.first_cycle = owner.getSession().current_cycle
        self.owner = owner
        self.other = other
        self.others_present = list()
        self.rating = None
        if str(other) not in owner.perceptions.keys():
            self.rating = owner['regard']['current']
            
        else:
            self.rating = owner.getRating(other)
        
        self.cycles_present = 1
        
        recorded_data = ('owner', 'others', 'total')
        
        self.data = {}
        for item in recorded_data:
            self.data[item] = {
                'count': 0, 'statements': 0,
                'avg positivity': 0, 'avg energy': 0, 
                'min positivity': 0, 'min energy': 0, 
                'max positivity': 0, 'max energy': 0,
                'first positivity': 0, 'first energy': 0,
                'last positivity': 0, 'last energy': 0}

    def __eq__(self, other):
        return self.rating == other.rating
        
    def __ne__(self, other):
        return self.rating != other.rating
        
    def __gt__(self, other):
        return self.rating > other.rating
        
    def __ge__(self, other):
        return self.rating >= other.rating
        
    def __lt__(self, other):
        return self.rating < other.rating
        
    def __le__(self, other):
        return self.rating <= other.rating
        
    def __getitem__(self, index):
        return self.data[index]
        
    def printStats(self):
        categories = self.data.keys()
        print "\tcycles_present: ", self.cycles_present
        for category in categories:
            print "\t%s: " % category,
            print self.data[category]['count'], "(count)",
            print self.data[category]['avg positivity'], "(avg positivity)", 
            print self.data[category]['avg energy'], "(avg energy)"
        print "\toverall rating: ", self.rating
        
    def addTransmission(self, transmission):
        self.others_present = [item for item in transmission.targets if item != self.owner]
            
        audience = ['total'] 
            
        if not self.owner in transmission.targets:
            audience.append('others')
            
        elif len(transmission.targets) == 1:
            audience.append('owner')
            
        for item in audience:
            self.data[item]['avg positivity'] = \
                newAverage(self.data[item]['count'], 
                self.data[item]['avg positivity'], transmission.positivity)
                
            self.data[item]['avg energy'] = \
                newAverage(self.data[item]['count'], 
                self.data[item]['avg energy'], transmission.energy)
                
            if self.data[item]['count'] == 0:
                self.data[item]['first positivity'] = transmission.positivity
                self.data[item]['first energy'] = transmission.energy
            self.data[item]['last positivity'] = transmission.positivity
            self.data[item]['last energy'] = transmission.positivity
            
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
            self.data[item]['count'] += 1
            
    def closeInteraction(self, leaving):
        self.cycles_present = 1 + (self.owner.getSession().current_cycle - self.first_cycle)
        interaction_guesses = {}
        
        if leaving != self.owner:
            # STAMINA
            interaction_guesses['stamina'] = (1.0 - (1/self.cycles_present)) * 99
            
        # COMMUNICATIVE
        # initial guess from data
        communicative_guess = float(self.data['total']['count']) / \
                            (float(self.cycles_present) * 20.0)
        interaction_guesses['communicative'] = communicative_guess * 99
                        
        # TALKATIVE
        if self.data['total']['count'] > 0:
            talkative_guess = float(self.data['total']['statements']) / \
                                float(self.data['total']['count']) * 99
            interaction_guesses['talkative'] = talkative_guess
        
        # POSITIVITY (possibly change average to first)
        interaction_guesses['positivity'] = float(self.data['total']['first positivity'])

        # ENERGY               
        interaction_guesses['energy'] = float(self.data['total']['first energy'])

        
        tolerance_threshold = self.owner['tolerance']['coefficient'] * 10
        tolerance_met = 0
        for key in interaction_guesses:
            print "%s guess: %f, desired: %f" % (key, interaction_guesses[key], self.owner.getDesired(key))
            delta = abs(self.owner.getDesired(key) - interaction_guesses[key])
            if delta <= tolerance_threshold:
                tolerance_met += 1
        print "tolerance_met: %d" % tolerance_met
        self.rating = float(tolerance_met / len(interaction_guesses)) * 99
        
        return self.rating

class session(object):
    def __init__(self):
        self.session_ID = randint(0, 10000)
        self.participants = list()
        self.current_cycle = 0
        self.session_open = True
        
    def __eq__(self, other):
        if other == None:
            return False
            
        else:
            return self.session_ID == other.session_ID
        
    def __ne__(self, other):
        return self.session_ID != other.session_ID
        
    def addParticipant(self, entering):
        entering.current_session = self
        for sb in self.participants:
            sb.addInteraction(entering)
            entering.addInteraction(sb)
            
        self.participants.append(entering)
        
    def getAllOthers(self, participant):
        other_participants = self.participants[:]
        other_participants.remove(participant)
        return other_participants
    
    def removeParticipant(self, leaving):
        other_participants = self.getAllOthers(leaving)
        for participant in other_participants:
            leaving.endInteraction(participant, leaving)
            participant.endInteraction(leaving, leaving)
    
        leaving.removeSession()
        self.participants.remove(leaving)
        
    def transmissionPhase(self, transmission_list):
        for participant in self.participants:
            if participant.proc('communicative'):
                available_targets = self.getAllOthers(participant)
                if len(available_targets) > 0:
                    transmission_list.append(participant.broadcast(available_targets))
                
    def interpretPhase(self, transmission_list):
        for participant in self.participants:
            for item in transmission_list:
                if participant != item.source:
                    participant.interpretTransmission(item)
                    
    def leavePhase(self):   
        leaving = list()
        for participant in self.participants:
            if not participant.proc('stamina'):
                leaving.append(participant)
            
        for participant in leaving:
            self.removeParticipant(participant)
                
        if len(self.participants) == 1:
            self.removeParticipant(self.participants[0])
            
        if len(self.participants) == 0:
            self.endPhase()
                
    def endPhase(self):
        self.session_open = False
                
    def cycle(self):
        for i in range(20):
            transmission_list = list()
            self.transmissionPhase(transmission_list)
            self.interpretPhase(transmission_list)
        
        self.leavePhase()
        self.current_cycle += 1
            
class community(object):
    def __init__(self):
        self.community_ID = randint(0, 100000)
        
        self.members = list()
        self.sessions = list()
        
    def addMember(self, new):
        self.members.append(new)
        new.addCommunity(self)
        
    def getAllOthers(self, member):
        other_members = self.members[:]
        other_members.remove(member)
        return other_members
        
    def createSession(self, first, second):
        new_session = session()
        new_session.addParticipant(first)
        new_session.addParticipant(second)
        self.sessions.append(new_session)
        
    def printMembers(self, traits=False, memory=False):
        for member in self.members:
            member.printInfo(traits=traits, memory=memory)
        
    def cycle(self):
        for session in self.sessions:
            session.cycle()
            
        void_sessions = [session for session in self.sessions if session.session_open == False]
        
        for session in void_sessions:
            self.sessions.remove(session)
            
        for member in self.members:
            if member.isAvailable():
                member.cycle()
