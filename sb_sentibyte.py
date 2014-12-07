from random import randrange, randint, choice, uniform
import random
from jep_loot.jeploot import catRoll, booRoll
from sb_communication import session, transmission, interaction
from sb_utilities import getCoefficient, calcInfluence, calcAccuracy, boundsCheck, weightedAverage
from heapq import heappush, heappop

random.seed()

class valueState(object):
    def __init__(self, lower_min=0.0, upper_max=99.0):
        self.params = {}
        span = boundsCheck(upper_max) - boundsCheck(lower_min)
        self.setBounds(boundsCheck(lower_min), span)
        self.setBase()
        self.params['current'] = float(self['base'])
        
        self.update()
        
    def __getitem__(self, index):
        return self.params[index]
        
    def __eq__(self, other):
        return int(self.params['current']) == int(other.params['current'])
        
    def __ne__(self, other):
        return int(self.params['current']) != int(other.params['current'])
        
    def update(self):
        delta = self['current'] - self['lower']
        value_range = self['upper'] - self['lower']
        self.params['relative'] = delta / value_range
        
        self.params['coefficient'] = self['current'] / 99.0
        
    def changeCurrent(self, value):
        self.params['current'] = value
        self.update()
        
    def proc(self):
        return random.random() < self['coefficient']
        
    def setBounds(self, lower_min, span):
        lower_bound_quadrants = {}
        lower_bound_quadrants[(lower_min + (.0 * span), lower_min + (.1 * span))] = 10
        lower_bound_quadrants[(lower_min + (.1 * span), lower_min + (.2 * span))] = 20
        lower_bound_quadrants[(lower_min + (.2 * span), lower_min + (.3 * span))] = 40
        lower_bound_quadrants[(lower_min + (.3 * span), lower_min + (.4 * span))] = 20
        lower_bound_quadrants[(lower_min + (.4 * span), lower_min + (.5 * span))] = 10
        lower_bound_quadrant = catRoll(lower_bound_quadrants)
        self.params['lower'] = uniform(lower_bound_quadrant[0], lower_bound_quadrant[1])
        
        upper_bound_quadrants = {}
        upper_bound_quadrants[(lower_min + (.5 * span), lower_min + (.6 * span))] = 10
        upper_bound_quadrants[(lower_min + (.6 * span), lower_min + (.7 * span))] = 20
        upper_bound_quadrants[(lower_min + (.7 * span), lower_min + (.8 * span))] = 40
        upper_bound_quadrants[(lower_min + (.8 * span), lower_min + (.9 * span))] = 20
        upper_bound_quadrants[(lower_min + (.9 * span), lower_min + span)] = 10
        upper_bound_quadrant = catRoll(upper_bound_quadrants)
        self.params['upper'] = uniform(upper_bound_quadrant[0], upper_bound_quadrant[1])
        
    def setBase(self):
        span = self['upper'] - self['lower']
        low = self['lower'] + (span * .1)
        span -= (span * .2)
        
        base_quadrants = {}
        base_quadrants[(low + (.0 * span), low + (.2 * span))] = 10
        base_quadrants[(low + (.2 * span), low + (.4 * span))] = 20
        base_quadrants[(low + (.4 * span), low + (.6 * span))] = 40
        base_quadrants[(low + (.6 * span), low + (.8 * span))] = 20
        base_quadrants[(low + (.8 * span), low + span)] = 10
        base_quadrant = catRoll(base_quadrants)
        self.params['base'] = uniform(base_quadrant[0], base_quadrant[1])
        
class perception(object):
    def __init__(self, perceived, owner):
        self.perceived = perceived
        self.owner = owner
        self.p_traits = {}
        self.entries = 0
        self.p_states = {}
        
        # assume other's traits and states are same as owner's, adjust for regard
        for key in owner.d_traits.keys():
            assumed_value = owner.i_traits[key]['base']
            self.p_traits[key] = self.guessValue(assumed_value)
            
        for key in owner.states.keys():
            assumed_value = owner[key]['base']
            self.p_states[key] = self.guessValue(assumed_value)
            
    def addInteraction(self, interaction):
        sb_ID = str(self.perceived)
        #self.i_traits['impressionability'] = valueState(2, 5)
        #self.i_traits['communication range'] = valueState(10, 90)
        #self.i_traits['energy range'] = valueState()
        #self.i_traits['talkative'] = valueState(10, 60)
        #self.i_traits['expressive'] = valueState()
        #self.i_traits['stamina'] = valueState(95, 99)
        #self.i_traits['sociable'] = valueState(10, 90)
        
        # initial guess from data
        talkative_guess = float(interaction.data['total']['count']) / \
                            float(interaction.rounds_present) * 100
        # adjust for regard
        talkative_guess = self.guessValue(talkative_guess)
        
        # update with weighted average           
        self.p_traits['talkative'] = weightedAverage(talkative_guess, interaction.rounds_present, 
                        self.p_traits['talkative'], self.entries)
                            
        self.entries += interaction.rounds_present
        
        #communicative = total / rounds present (modified for perceptiveness)
        #talkative = total statements / rounds present (modified for perceptiveness)
        #expressive = total body language / rounds present (modified for perceptiveness)
        #communication range = (((max - avg) + (avg - min)) / 2) / 100 (modified for perceptiveness)
        #engergy range = " " " " " "
        pass
            
    def guessValue(self, assumed_value):
        regard_offset = (self.owner['regard']['coefficient'] - .5) * 100
        adjusted_value = boundsCheck(assumed_value + regard_offset)
        return (assumed_value + adjusted_value) / 2 
            
    def printPerception(self):
        print "%s perception of %s...." % (self.owner, self.perceived),
        print "(%d entries)" % (self.entries)
        
        for key in self.p_states.keys():
            print "\t%s: %f" % (key, self.p_states[key])
            
        for key in self.p_traits.keys():
            print "\t%s: %f" % (key, self.p_traits[key])
            
        
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
        self.net_mood_change = float(0)
        self.net_communication_change = float(0)
        
        # mood states
        self.states = {}
        self.states['positivity'] = valueState()
        self.states['regard'] = valueState()
        self.states['energy'] = valueState()
        
        # personal characteristics
        self.p_traits = {}
        self.p_traits['volatility'] = valueState(5, 55)
        self.p_traits['moodiness'] = valueState(2, 20)
        self.p_traits['perception range'] = valueState()
        self.p_traits['observant'] = valueState()
        self.p_traits['tolerance'] = valueState() #sets threshold for others corresponding to desired
        self.p_traits['reflectiveness'] = valueState() #chance to review memory
        
        # interpersonal characteristics
        self.i_traits = {}
        self.i_traits['impressionability'] = valueState(2, 5)
        self.i_traits['communication range'] = valueState(10, 90)
        self.i_traits['energy range'] = valueState()
        self.i_traits['talkative'] = valueState(10, 60)
        self.i_traits['expressive'] = valueState()
        self.i_traits['stamina'] = valueState(95, 99)
        self.i_traits['sociable'] = valueState(10, 90)
        
        # desired interpersonal characteristics of others
        self.d_traits = {}
        self.d_traits['impressionability'] = valueState(2, 5)
        self.d_traits['communication range'] = valueState(10, 90)
        self.d_traits['energy range'] = valueState()
        self.d_traits['talkative'] = valueState(10, 60)
        self.d_traits['expressive'] = valueState()
        self.d_traits['stamina'] = valueState(95, 99)
        self.d_traits['sociable'] = valueState(10, 90)
        
        # other characteristics
        #self.traits['manipulative'] = valueState() #increases bonds with impressionable others
        
        # social characteristics
        #self.traits['friend preference'] = valueState() # procs connection to friend
        
    def __getitem__(self, index):
        return self.states[index]
        
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
            
        elif trait in self.states.keys():
            return self.states[trait].proc()
            
        else:
            print "key not found"
            return False
        
    def isAvailable(self):
        return self.current_session == None
            
    def addCommunity(self, new):
        if self.community == None:
            self.community = new
            
    def removeSession(self):
        self.current_session = None
        
    def observeOther(self, other):
        pass
    
    def incrementInteractions(self):
        for item in self.current_interactions:
            self.current_interactions[item].rounds_present += 1
            
    def interpretTransmission(self, sent):
        source = str(sent.source)
        
        self.current_interactions[source].addTransmission(sent)
        if self in sent.targets:
            self.receiveTransmission(sent)
            
    def addInteraction(self, other):
        toAdd = interaction(self, other)
        
        sb_ID = str(other)
        self.current_interactions[sb_ID] = toAdd
        
        if sb_ID not in self.perceptions.keys():
            self.perceptions[sb_ID] = perception(other, self)
            self.observeOther(other)
        
    def endInteraction(self, other):
        sb_ID = str(other)
        target = self.current_interactions[sb_ID]
        
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
        original_positivity = self['positivity']['current']
        positivity_change = calcInfluence(self['positivity']['current'], received.positivity, 
                            self.i_traits['impressionability']['coefficient'])
        self['positivity'].changeCurrent(original_positivity + positivity_change)
        self.net_communication_change += self['positivity']['current'] - original_positivity
        
    def broadcast(self, targets):
        positivity = calcAccuracy(self['positivity']['current'], self.i_traits['communication range']['coefficient'])
        energy = calcAccuracy(self['energy']['current'], self.i_traits['energy range']['coefficient'])
            
        return transmission(self, choice(targets), positivity, energy)
        
    def moodChange(self):
        original_positivity = self['positivity']['current']
        positive_chance = float(0)
        
        if self['positivity']['current'] >= self['positivity']['base']:
            dist_from_upper = self['positivity']['upper'] - self['positivity']['current']
            upper_range = self['positivity']['upper'] - self['positivity']['base']
            positive_chance = (dist_from_upper/upper_range) * .5
            
        else:
            dist_from_lower = self['positivity']['current'] - self['positivity']['lower']
            lower_range = self['positivity']['base'] - self['positivity']['lower']
            positive_chance = 1 - ((dist_from_lower/lower_range) * .5)
            
        
        positivity_change = self.p_traits['moodiness']['coefficient'] * \
                    (self['positivity']['upper'] - self['positivity']['lower'])
        
        if not booRoll(positive_chance):
            positivity_change *= -1
            
        self['positivity'].changeCurrent(original_positivity + positivity_change)
        if self['positivity']['current'] > self['positivity']['upper']:
            self['positivity'].changeCurrent(float(self['positivity']['upper']))
                
        elif self['positivity']['current'] < self['positivity']['lower']:
            self['positivity'].changeCurrent(float(self['positivity']['lower']))
            
        self.net_mood_change += self['positivity']['current'] - original_positivity
                    
    def cycle(self):
        if self.proc('volatility'):
            self.moodChange()
            
        if self.proc('sociable'):
            self.joinSession()
            
    def chooseOther(self, members):
        return choice(members)
            
    def joinSession(self):
        available_sessions = self.community.sessions[:]
        if len(available_sessions) == 0:
            members_available = [member for member in \
                        self.community.getAllOthers(self) \
                        if member.isAvailable()]
            
            chosen = self.chooseOther(members_available)
            self.community.createSession(self, chosen)
            
        else:
            choice(available_sessions).addParticipant(self)
        
    def printInfo(self, traits=False):
        print "unique ID: ", self.sentibyte_ID
        print "name: ", self.name
        
        for state in self.states:
            print "%s: %f" % (state, self.states[state]['current'])
            
        print "net_mood_change: ", self.net_mood_change
        print "net_communication_change: ", self.net_communication_change
        print "net change: ", self.net_communication_change + self.net_mood_change
        print "current session: ", self.current_session
        
        if len(self.perceptions) > 0:
            print "current perceptions: "
            for key in self.perceptions:
                self.perceptions[key].printPerception()
        
        if len(self.current_interactions) > 0:
            print "current interactions: "
            for item in self.current_interactions:
                print "%s......" % item
                self.current_interactions[item].printStats()
                
        if len(self.memory) > 0:
            print "memory: "
            for item in self.memory:
                print "%s......" % item
                for log in self.memory[item]:
                    log.printStats()
                    print '-' * 4
        
        if traits:       
            self.printTraits()
        
    def printTraits(self):
        print "personal traits..."
        for trait in self.p_traits:
            print "\t%s: %f" % (trait, self.p_traits[trait]['coefficient'])
        print "interpersonal traits..."
        for trait in self.i_traits:
            print "\t%s: %f" % (trait, self.i_traits[trait]['coefficient'])
        print "desired traits..."
        for trait in self.d_traits:
            print "\t%s: %f" % (trait, self.d_traits[trait]['coefficient'])
        print '-' * 10
        
    def printConnections(self):
        print '-' * 10
        for i in range(len(self.perceptions)):
            print "connection %d..." % i
            self.perceptions[i].printInfo()
        
    def setPositivity(self, upper=-1, lower=-1, base=-1, current=-1):
        temp_upper = self['positivity']['upper']
        temp_lower = self['positivity']['lower']
        temp_base = self['positivity']['base']
        temp_current = self['positivity']['current']
        
        if upper != -1:
            temp_upper = upper
        if lower != -1:
            temp_lower = lower
        if base != -1:
            temp_base = base
        if current != -1:
            temp_current = current
            
        if temp_current < temp_lower or temp_current > temp_upper or \
            temp_base < temp_lower or temp_base > temp_upper:
                print "invalid bounds"
            
        else:
            self['positivity']['upper'] = temp_upper
            self['positivity']['lower'] = temp_lower
            self['positivity']['base'] = temp_base
            self['positivity']['current'] = temp_current
            
    def setRegard(self, upper=-1, lower=-1, base=-1, current=-1):
        temp_upper = self.regard_upper_bound
        temp_lower = self.regard_lower_bound
        temp_base = self.regard_base
        temp_current = self.regard_current
        
        if upper != -1:
            temp_upper = upper
        if lower != -1:
            temp_lower = lower
        if base != -1:
            temp_base = base
        if current != -1:
            temp_current = current
            
        if temp_current < temp_lower or temp_current > temp_upper or \
            temp_base < temp_lower or temp_base > temp_upper or \
            temp_lower < 0 or temp_upper > 99:
                print "invalid bounds"
            
        else:
            self.regard_upper_bound = temp_upper
            self.regard_lower_bound = temp_lower
            self.regard_base = temp_base
            self.regard_current = temp_current
            