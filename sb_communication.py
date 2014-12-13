from random import random, randint
from sb_utilities import newAverage

class transmission(object):
    def __init__(self, source, targets, positivity, energy, t_type, information):
        self.positivity = positivity
        self.energy = energy
        self.source = source
        self.targets = targets[:]
        self.t_type = t_type
        self.information = information
        
    def printStats(self):
        print "TESTING"

class interaction(object):
    def __init__(self, owner, other, session):
        self.session = session
        self.first_cycle = self.session.current_cycle
        self.owner = owner
        self.other = other
        self.others_present = list()
        self.overall_rating = None
        if str(other) not in owner.perceptions.keys():
            self.overall_rating = owner['regard']['current']
            
        else:
            self.overall_rating = owner.getRating(other)
        
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

    def __eq__(self, other):
        if self.cycles_present < 4:
            return self.cycles_present == other.cycles_present
        else:
            return self.overall_rating == other.overall_rating
        
    def __ne__(self, other):
        if self.cycles_present < 4:
            return self.cycles_present != other.cycles_present
        else:
            return self.overall_rating != other.overall_rating
        
    def __gt__(self, other):
        if self.cycles_present < 4:
            return self.cycles_present > other.cycles_present
        else:
            return self.overall_rating > other.overall_rating
        
    def __ge__(self, other):
        if self.cycles_present < 4:
            return self.cycles_present >= other.cycles_present
        else:
            return self.overall_rating >= other.overall_rating
        
    def __lt__(self, other):
        if self.cycles_present < 4:
            return self.cycles_present < other.cycles_present
        else:
            return self.overall_rating < other.overall_rating
        
    def __le__(self, other):
        if self.cycles_present < 4:
            return self.cycles_present <= other.cycles_present
        else:
            return self.overall_rating <= other.overall_rating
        
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
        print "\toverall rating: ", self.overall_rating
        
    def addTransmission(self, transmission):
        # adjust stamina levels based on mood, stay longer for good results
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
        
            if transmission.information != None:
                self.data[item]['declarations'] +=1
        
            self.data[item]['count'] += 1
            
            self.updateInteraction()
            
    def updateInteraction(self):
        # adjusted
        self.cycles_present = 1 + (self.owner.getSession().current_cycle - self.first_cycle)
            
        # COMMUNICATIVE
        # initial guess from data
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
        
        # POSITIVITY (possibly change average to first)
        self.g_traits['positivity'] = float(self.data['total']['first positivity'])

        # ENERGY               
        self.g_traits['energy'] = float(self.data['total']['first energy'])
        
        #print '-' * 5
        #print "%s interpretation of interaction" % self.owner
        ratings = list()
        for key in self.g_traits:
            delta = abs(self.owner.getDesired(key) - self.g_traits[key])
            rating = 99 - float(delta)
            priority = self.owner.desire_priority[key]
            for i in range(priority):
                ratings.append(rating)
            #print "%s guess: %f, desired: %f, actual: %f, rating: %f" % (key, self.g_traits[key], self.owner.getDesired(key), self.other[key]['current'], rating)
        
        self.overall_rating = float(sum(ratings)) / float(len(ratings))
        
        #print "overall rating: %f" % self.overall_rating
        #print '-' * 5
        return self.overall_rating

class session(object):
    def __init__(self):
        self.session_ID = randint(0, 10000)
        self.participants = list()
        self.current_cycle = 0
        self.session_open = True
        self.communications_per_cycle = 12
        
    def __eq__(self, other):
        if other == None:
            return False
            
        else:
            return self.session_ID == other.session_ID
        
    def __ne__(self, other):
        return self.session_ID != other.session_ID
        
    def addParticipant(self, entering):
        #print "%s joins session %d" % (entering, self.session_ID)
        entering.current_session = self
        for sb in self.participants:
            sb.addInteraction(entering)
            entering.addInteraction(sb)
            
        self.participants.append(entering)
        
    def getAllOthers(self, participant):
        other_participants = [p for p in self.participants if p != participant]
        #other_participants.remove(participant)
        return other_participants
    
    def removeParticipant(self, leaving):
        #print "%s leaves session %d" % (leaving, self.session_ID)
        other_participants = self.getAllOthers(leaving)
        for participant in other_participants:
            leaving.endInteraction(participant)
            participant.endInteraction(leaving)
    
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
        #
        for i in range(self.communications_per_cycle):
            transmission_list = list()
            self.transmissionPhase(transmission_list)
            self.interpretPhase(transmission_list)
        
        self.current_cycle += 1
        self.leavePhase()
        
class community(object):
    def __init__(self):
        self.community_ID = randint(0, 100000)
        
        self.members = list()
        self.sessions = list()
        
    def addMember(self, new):
        for member in self.members:
            #member.addPerception(new)
            #new.addPerception(member)
            pass
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
        
    def printMembers(self, traits=False, memory=False, perceptions=False, friends=False):
        for member in self.members:
            member.printInfo(traits=traits, memory=memory, perceptions=perceptions, friends=friends)
        
    def cycle(self):
        for session in self.sessions:
            session.cycle()
            
        void_sessions = [session for session in self.sessions if session.session_open == False]
        
        for session in void_sessions:
            self.sessions.remove(session)
            
        for member in self.members:
            if member.isAvailable():
                member.cycle()
