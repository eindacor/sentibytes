from random import random, randint
from sb_utilities import newAverage

class transmission(object):
    def __init__(self, source, targets, positivity, energy):
        self.positivity = positivity
        self.energy = energy
        self.source = source
        self.targets = list()
        self.targets.append(targets)
        
    def printStats(self):
        print "TESTING"

class interaction(object):
    def __init__(self, owner, other):
        self.owner = owner
        self.other = other
        
        self.rounds_present = 0
        
        recorded_data = ('owner', 'others', 'total')
        
        self.data = {}
        for item in recorded_data:
            self.data[item] = {
                'count': 0, 'avg positivity': 0, 'avg energy': 0, 'min': 0, 'max': 0}
            
        self.priority = 0
        
        self.rating = float(50)
            
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
        
    def printStats(self):
        categories = self.data.keys()
        print "\trounds_present: ", self.rounds_present
        for category in categories:
            print "\t%s: " % category,
            print self.data[category]['count'], "(count)",
            print self.data[category]['avg positivity'], "(avg positivity)", 
            print self.data[category]['avg energy'], "(avg energy)"
        
    def addTransmission(self, transmission):
        if not self.owner in transmission.targets:
            self.data['others']['avg positivity'] = \
                newAverage(self.data['others']['count'], 
                self.data['others']['avg positivity'], transmission.positivity)
                
            self.data['others']['avg energy'] = \
                newAverage(self.data['others']['count'], 
                self.data['others']['avg energy'], transmission.energy)
            
            self.data['others']['count'] += 1
                
        elif len(transmission.targets) == 1:
            self.data['owner']['avg positivity'] = \
                newAverage(self.data['owner']['count'], 
                self.data['owner']['avg positivity'], transmission.positivity)
            
            self.data['owner']['avg energy'] = \
                newAverage(self.data['owner']['count'], 
                self.data['owner']['avg energy'], transmission.energy)
            
            self.data['owner']['count'] += 1
            
        self.data['total']['avg positivity'] = \
            newAverage(self.data['total']['count'], 
                        self.data['total']['avg positivity'], 
                        transmission.positivity)
                        
        self.data['total']['avg energy'] = \
            newAverage(self.data['total']['count'], 
                        self.data['total']['avg energy'], 
                        transmission.energy)
            
        self.data['total']['count'] += 1
        
    def interpretInteraction(self):
        pass

class session(object):
    def __init__(self):
        self.session_ID = randint(0, 10000)
        self.participants = list()
        self.cycles = 0
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
            leaving.endInteraction(participant)
            participant.endInteraction(leaving)
    
        leaving.removeSession()
        self.participants.remove(leaving)
        
    def transmissionPhase(self, transmission_list):
        for participant in self.participants:
            if participant.proc('talkative'):
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
        transmission_list = list()
        
        self.transmissionPhase(transmission_list)
        self.interpretPhase(transmission_list)
        
        for participant in self.participants:
            participant.incrementInteractions()
        
        self.leavePhase()
        
        self.cycles += 1
            
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
        
    def printMembers(self):
        for member in self.members:
            member.printInfo(traits=True)
        
    def cycle(self):
        for session in self.sessions:
            session.cycle()
            
        void_sessions = [session for session in self.sessions if session.session_open == False]
        
        for session in void_sessions:
            self.sessions.remove(session)
            
        for member in self.members:
            if member.isAvailable():
                member.cycle()
