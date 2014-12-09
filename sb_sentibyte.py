from random import randrange, randint, choice, uniform
import random
from jep_loot.jeploot import catRoll
from sb_communication import session, transmission, interaction
from sb_utilities import getCoefficient, calcInfluence, calcAccuracy, boundsCheck, weightedAverage, valueState
from sb_perception import perception
from heapq import heappush, heappop

random.seed()
            
class sentibyte(object):
    def __init__(self, user):
        self.user_ID = user
        self.name = randint(0, 1000000)
        self.location = randint(0, 10)
        
        self.sentibyte_ID = str(self.user_ID) + '.' + str(self.name)
        
        self.memory = {} #dict of lists of interaction logs, key = sentibyte_ID
        self.perceptions = {}
        self.current_session = None
        self.community = None
        self.current_interactions = {}
        
        # personal characteristics
        self.p_traits = {}
        self.p_traits['regard'] = valueState()
        self.p_traits['volatility'] = valueState(5, 55)
        self.p_traits['sensitivity'] = valueState(10, 90)
        self.p_traits['observant'] = valueState(70, 99)
        self.p_traits['pickiness'] = valueState() #determines likelihood of picking favored contacts
        self.p_traits['sociable'] = valueState(10, 90)
        self.p_traits['impressionability'] = valueState(1, 15)
        self.p_traits['tolerance'] = valueState(5, 95)
        self.p_traits['positivity range'] = valueState(10, 90)
        self.p_traits['energy range'] = valueState(10, 90)
        
        # interpersonal characteristics
        self.i_traits = {}
        self.i_traits['positivity'] = valueState()
        self.i_traits['energy'] = valueState()
        self.i_traits['talkative'] = valueState(10, 90)
        self.i_traits['stamina'] = valueState(50, 90)
        self.i_traits['communicative'] = valueState(10, 90)
        
        # desired interpersonal characteristics of others
        self.d_traits = {}
        self.d_traits['positivity'] = valueState()
        self.d_traits['energy'] = valueState()
        self.d_traits['talkative'] = valueState(10, 90) #chance for broadcast to be statement
        self.d_traits['stamina'] = valueState(50, 90)
        self.d_traits['communicative'] = valueState(10, 90) #chance to broadcast
        
        # other characteristics
        #self.traits['manipulative'] = valueState() #increases bonds with impressionable others
        
        # social characteristics
        #self.traits['friend preference'] = valueState() # procs connection to friend
        
    def __getitem__(self, index):
        if index in self.p_traits.keys():
            return self.p_traits[index]
            
        elif index in self.i_traits.keys():
            return self.i_traits[index]
            
        else:
            print "trait (%s) not found" % index
            return None
        
    def __eq__(self, other):
        return self.sentibyte_ID == other.sentibyte_ID
        
    def __ne__(self, other):
        return self.sentibyte_ID != other.sentibyte_ID
        
    def __str__(self):
        return self.sentibyte_ID
        
    def proc(self, trait):
        if trait in self.p_traits.keys():
            return self.p_traits[trait].proc()
            
        elif trait in self.i_traits.keys():
            return self.i_traits[trait].proc()
            
        else:
            print "trait (%s) not found" % trait
            return False
            
    def getSession(self):
        return self.current_session
        
    def isAvailable(self):
        return self.current_session == None
            
    def addCommunity(self, new):
        if self.community == None:
            self.community = new
            
    def removeSession(self):
        self.current_session = None
            
    def interpretTransmission(self, sent):
        source = str(sent.source)
        
        # add modifiers for interpretation
        if sent.t_type == 'statement' or self.proc('observant'):
            self.current_interactions[source].addTransmission(sent)
            
            if self in sent.targets:
                self.receiveTransmission(sent)
        
    def addPerception(self, other):
        self.perceptions[str(other)] = perception(other, self)
            
    def addInteraction(self, other):
        toAdd = interaction(self, other)
        
        sb_ID = str(other)
        self.current_interactions[sb_ID] = toAdd
        
        if sb_ID not in self.perceptions.keys():
            self.addPerception(other)
        
    def endInteraction(self, other, terminator):
        sb_ID = str(other)
        target = self.current_interactions[sb_ID]
        target.closeInteraction(terminator)
        
        # add to perception
        self.perceptions[sb_ID].addInteraction(target)
        
        # add to memory
        if sb_ID not in self.memory.keys():
            self.memory[sb_ID] = list()
            
        heappush(self.memory[sb_ID], self.current_interactions[sb_ID])
        
        if len(self.memory[sb_ID]) > 10:
            heappop(self.memory[sb_ID])
        
        # remove from interactions
        self.current_interactions.pop(sb_ID, None)
        
    def receiveTransmission(self, received):
        self['positivity'].influence(received.positivity)
        
    def broadcast(self, targets):
        positivity = calcAccuracy(self['positivity']['current'], self.p_traits['positivity range']['coefficient'])
        energy = calcAccuracy(self['energy']['current'], self.p_traits['energy range']['coefficient'])
        t_type = None
        if self.proc('talkative'):
            t_type = 'statement'
        else:
            t_type = 'signal'
            
        toSend = transmission(self, choice(targets), positivity, energy, t_type)
        return toSend
                    
    def cycle(self):
        if self.proc('volatility'):
            for trait in self.p_traits:
                self.p_traits[trait].fluctuate()
                
            for trait in self.d_traits:
                self.d_traits[trait].fluctuate()
                
            for trait in self.i_traits:
                self.i_traits[trait].fluctuate()
            
        if self.proc('sociable'):
            if not self.joinSession():
                self['positivity'].influence(self['positivity']['lower'])
            
    def wantsToContact(self, other):
        regard_threshold = self['tolerance']['coefficient'] * 10
        min_required = self['regard']['current'] - regard_threshold
        min_required = boundsCheck(min_required)
        
        return self.getRating(other) >= min_required
            
    def joinSession(self):
        perception_list = list()
        for member in self.community.getAllOthers(self):
            if str(member) not in self.perceptions.keys():
                self.addPerception(member)

            if self.wantsToContact(member):
                perception_list.append(self.perceptions[str(member)])
               
        if len(perception_list) == 0:
            return False
               
        perception_list.sort()
        weighed_options = {}
        for i in range(len(perception_list)):
            sb = perception_list[i].perceived
            index = i + 1
            weighed_options[sb] = index * self.p_traits['pickiness']['current']
           
        selected = catRoll(weighed_options)
        
        while self.contact(selected) == False:
            del weighed_options[selected]
            
            if len(weighed_options) == 0:
                return False
         
            selected = catRoll(weighed_options)
                
        return True
        
    def getRating(self, other):
        sb_ID = str(other)
        if sb_ID not in self.perceptions.keys():
            return None
        else:
            return self.perceptions[sb_ID].getCurrent()
            
    def getDesired(self, trait):
        return self.d_traits[trait]['current']
        
    def contact(self, other):
        # add more parameters for relationship quality, determine rejection/reaction
        if str(self) not in other.perceptions.keys():
            other.addPerception(self)
        
        if not other.wantsToContact(self):
            self.perceptions[str(other)].addRejection()
        
        elif other.proc('sociable'):
            self.perceptions[str(other)].addAcceptance()
            if other.current_session == None:
                self.community.createSession(self, other)
                return True
                
            else:
                other.current_session.addParticipant(self)
                return True
                
        elif self.proc('sensitivity'):
            print "sensitivity proc'ed"
            self.perceptions[str(other)].addRejection()
            
        else:
            self.perceptions[str(other)].addUnavailable()
        
    def printInfo(self, traits=False, memory=False):
        print '-' * 10
        print "unique ID: ", self.sentibyte_ID
        print "name: ", self.name
        print "current session: ", self.current_session
        
        if traits:       
            self.printTraits()
        
        if len(self.perceptions) > 0:
            print "current perceptions: "
            for key in self.perceptions:
                self.perceptions[key].printPerception()
         
        if len(self.memory) > 0 and memory == True:
            print "memory: "
            for item in self.memory:
                print "%s......" % item
                for log in self.memory[item]:
                    log.printStats()
                    print '-' * 4
        
    def printTraits(self):
        print "personal traits..."
        for trait in self.p_traits:
            print "\t%s: %f" % (trait, self.p_traits[trait]['current'])
        print "interpersonal traits..."
        for trait in self.i_traits:
            print "\t%s: %f" % (trait, self.i_traits[trait]['current'])
        print "desired traits..."
        for trait in self.d_traits:
            print "\t%s: %f" % (trait, self.d_traits[trait]['current'])
        
    def printConnections(self):
        print '-' * 10
        for i in range(len(self.perceptions)):
            print "connection %d..." % i
            self.perceptions[i].printInfo()
            