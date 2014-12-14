from random import randrange, randint, choice, uniform, shuffle
import random
from jep_loot.jeploot import catRoll
from sb_communication import session, transmission, interaction
from sb_utilities import getCoefficient, calcInfluence, calcAccuracy, boundsCheck, weightedAverage, valueState
from sb_perception import perception
from heapq import heappush, heappop
            
class sentibyte(object):
    def __init__(self, user, the_truth):
        self.user_ID = user
        self.name = randint(0, 1000000)
        self.location = randint(0, 10)
        
        self.sentibyte_ID = str(self.user_ID) + '.' + str(self.name)
        
        self.memory = {} #dict of lists of interaction logs, key = sentibyte_ID
        self.perceptions = {}
        self.current_session = None
        self.community = None
        self.current_interactions = {}
        self.friend_list = list()
        self.contacts = {}
        self.knowledge = {}
        self.the_truth = the_truth
        self.learned_on_own = 0
        self.learned_from_others = 0
        self.met_through_others = 0
        self.invitations_to_friends = 0
        self.invitations_to_contacts = 0
        self.invitaitons_to_strangers = 0
        
        # personal characteristics
        self.p_traits = {}
        self.p_traits['regard'] = valueState(10, 90)
        self.p_traits['volatility'] = valueState(5, 25)
        self.p_traits['sensitivity'] = valueState(5, 20)
        self.p_traits['observant'] = valueState(70, 99)
        # pickiness determines likelihood of picking favored contacts
        self.p_traits['pickiness'] = valueState(40, 99)
        self.p_traits['impressionability'] = valueState(1, 15)
        self.p_traits['tolerance'] = valueState()
        self.p_traits['positivity_range'] = valueState(10, 90)
        self.p_traits['energy_range'] = valueState(10, 90)
        self.p_traits['adventurous'] = valueState(0, 50)
        self.p_traits['private'] = valueState()
        self.p_traits['reflective'] = valueState()
        self.p_traits['trusting'] = valueState()
        self.p_traits['stamina'] = valueState()
        
        # interpersonal characteristics
        self.i_traits = {}
        self.i_traits['positivity'] = valueState()
        self.i_traits['energy'] = valueState()
        self.i_traits['talkative'] = valueState(10, 90)
        self.i_traits['communicative'] = valueState(10, 90)
        self.i_traits['sociable'] = valueState(10, 99)
        self.i_traits['intellectual'] = valueState(0, 50)
        
        # desired interpersonal characteristics of others
        self.d_traits = {}
        self.d_traits['positivity'] = valueState()
        self.d_traits['energy'] = valueState()
        # talkative chance for broadcast to be statement
        self.d_traits['talkative'] = valueState(10, 90) 
        # communicative determines likelihood of broadcasting while interacting
        self.d_traits['communicative'] = valueState(10, 90) 
        self.d_traits['sociable'] = valueState(10, 99)
        self.d_traits['intellectual'] = valueState()
        
        desired_list = self.d_traits.keys()
        shuffle(desired_list)
        self.desire_priority = {}
        for i in range(len(desired_list)):
            priority = i + 1
            self.desire_priority[desired_list[i]] = priority
        
        self.learn()
        
    def __getitem__(self, index):
        if index in self.p_traits:
            return self.p_traits[index]
            
        elif index in self.i_traits:
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
        if trait in self.p_traits:
            return self.p_traits[trait].proc()
            
        elif trait in self.i_traits:
            return self.i_traits[trait].proc()
            
        else:
            print "trait (%s) not found" % trait
            return False
            
    def getCurrent(self, index):
        if index in self.p_traits:
            return self.p_traits[index].params['current']
            
        elif index in self.i_traits:
            return self.i_traits[index].params['current']

        else:
            print "trait (%s) not found" % index
            return None
            
    def getSession(self):
        return self.current_session
        
    def isAvailable(self):
        return self.current_session == None
            
    def addCommunity(self, new):
        if self.community == None:
            self.community = new
            
    def removeSession(self):
        self.current_session = None
        self.i_traits['positivity'].params['current'] = self['positivity']['base'] 
            
    def interpretTransmission(self, sent):
        source = str(sent.source)
        
        # add modifiers for interpretation
        if sent.t_type == 'statement' or self.proc('observant'):
            self.current_interactions[source].addTransmission(sent)
            
            if self in sent.targets:
                self.receiveTransmission(sent)
        
    def addPerception(self, other):
        if str(other) not in self.perceptions:
            self.perceptions[str(other)] = perception(other, self)
           
    def addInteraction(self, other):
        self.addPerception(other)
        
        toAdd = interaction(self, other, self.current_session)
        
        sb_ID = str(other)
        self.current_interactions[sb_ID] = toAdd
            
        if str(other) not in self.contacts:
            self.contacts[str(other)] = other
        
    def updateFriends(self):
        num_friends = 12
        
        perception_list = [self.perceptions[p] for p in self.contacts]
    
        perception_list.sort()
        
        length = len(perception_list)
        
        if length > num_friends:
            perception_list = perception_list[length - num_friends:]
            
        self.friend_list = [str(p.perceived) for p in perception_list]
                
    def getFriends(self):
        self.updateFriends()
        friends = [self.contacts[sb_ID] for sb_ID in self.friend_list]
        return friends
    
    def getStrangers(self):
        stranger_list = [m for m in self.community.members 
                        if m != self and str(m) not in self.memory]
              
        return stranger_list
        
    def getContacts(self):
        return self.contacts.values()
        
    def getContact(self, sb_ID):
        return self.contacts[sb_ID]
        
    def endInteraction(self, other):
        sb_ID = str(other)
        target = self.current_interactions[sb_ID]
        target.updateInteraction()
        
        # add to perception
        self.perceptions[sb_ID].addInteraction(target)
        
        # add to memory
        if sb_ID not in self.memory:
            self.memory[sb_ID] = list()
            
        heappush(self.memory[sb_ID], self.current_interactions[sb_ID])
        
        if len(self.memory[sb_ID]) > 10:
            heappop(self.memory[sb_ID])
        
        # remove from interactions
        self.current_interactions.pop(sb_ID, None)
        
    def receiveTransmission(self, received):
        self['positivity'].influence(received.positivity)
        self['energy'].influence(received.energy)
        
        if received.information != None and self.proc('trusting') and self.proc('intellectual'):
            index = received.information[0]
            data = received.information[1]
            if index not in self.knowledge:
                self.knowledge[index] = data
                self.learned_from_others += 1
        
    def broadcast(self, targets):
        positivity_current = self['positivity']['current']
        positivity_co = self.p_traits['positivity_range']['coefficient']
        positivity = calcAccuracy(positivity_current, positivity_co)
        energy_current = self['energy']['current']
        energy_co = self.p_traits['energy_range']['coefficient']
        energy = calcAccuracy(energy_current, energy_co)
        t_type = None
        information = None
        if self.proc('talkative'):
            t_type = 'statement'
            
            if self.proc('intellectual'):
                index = choice(self.knowledge.keys())
                data = self.knowledge[index]
                
                information = [index, data]
        else:
            t_type = 'signal'
            
        # add preference for talking to different people
        selected_targets = list()
        
        while self.proc('sociable'):
            for other in targets:
                if self.wantsToContact(other) and other not in selected_targets:
                    selected_targets.append(other)
            
        if len(selected_targets) == 0:
            selected_targets.append(choice(targets))
            
        toSend = transmission(self, selected_targets, positivity, 
                                energy, t_type, information)
        return toSend
        
    def reflect(self):
        # add modifier for positivity
        pass
    
    def learn(self):
        if len(self.knowledge) != len(self.the_truth):
            unknown = [i for i in self.the_truth if i not in self.knowledge]
            new_index = choice(unknown)
            
            self.knowledge[new_index] = self.the_truth[new_index]
            self.learned_on_own += 1
        
    def cycle(self):
        if self.proc('volatility'):
            for trait in self.p_traits:
                self.p_traits[trait].fluctuate()
                
            for trait in self.d_traits:
                self.d_traits[trait].fluctuate()
                
            for trait in self.i_traits:
                self.i_traits[trait].fluctuate()
                
        if self.proc('reflective'):
            self.reflect()
            
        if self.proc('sociable'):
            if not self.joinSession():
                self['positivity'].influence(self['positivity']['lower'])
                
        if self.proc('intellectual'):
            self.learn()
            
    def joinSession(self):
        self.updateFriends()
        # generate list of targets (strangers, contacts, or friends)
        target_list = list()
        if self.proc('adventurous') or len(self.friend_list) == 0:
            target_list = self.getStrangers()
            self.invitaitons_to_strangers += 1
            
        elif self.proc('pickiness'):
            target_list = self.getFriends()
            self.invitations_to_friends += 1
        
        else:
            target_list = self.getContacts()
            self.invitations_to_contacts += 1
        
        target_list = [sb for sb in target_list if self.wantsToContact(sb)]
        
        weighed_options = {}
        for other in target_list:
            if str(other) in self.perceptions:
                weighed_options[other] = self.getRating(str(other), relative=True)
            else:
                weighed_options[other] = self['regard']['current']
            
        if len(weighed_options) == 0:
            return False
            
        selected = catRoll(weighed_options)
        
        # keep contacting until there are no targets left or succcessful connecction
        while self.contact(selected) == False:
            del weighed_options[selected]
            
            if len(weighed_options) == 0:
                return False
         
            selected = catRoll(weighed_options)
         
        return True
        
    # returns rating of particular sentibyte by ID or object
    # if the target is yet to make contact with self, returns self's current
    # regard level
    def getRating(self, other, relative=False):
        if type(other) == sentibyte:
            other = other.sentibyte_ID
            
        if other not in self.perceptions:
            rating = self['regard']['current']
        
        else:
            rating = self.perceptions[other].rating
        
        if relative:
            regard_range = self['regard']['upper'] - self['regard']['lower']
            delta_to_min = rating - self['regard']['lower']
            rating = float(delta_to_min) / float(regard_range)
            rating *= 99
            
        return rating
            
    def getDesired(self, trait):
        return self.d_traits[trait]['current']
    
    # must be separate from "contact" function to filter out potential contact attempts
    # not just for denying invitations, also for determining who to invite
    def wantsToContact(self, other):
        regard_threshold = self['tolerance']['coefficient'] * 10
        threshold_min = self['regard']['current'] - regard_threshold
        return self.getRating(str(other)) >= threshold_min
       
    # returns true if a session is successfully joined or created
    def contact(self, other):
        other.addPerception(self)
        self.addPerception(other)
        other.perceptions[str(self)].addInvitation()
        
        if not other.wantsToContact(self):
            self.perceptions[str(other)].addRejection()
            
        elif type(other.current_session) != type(None) and len(other.current_session.participants) > 10:
            self.perceptions[str(other)].addUnavailable()
            return False
        
        elif other.proc('sociable'):
            self.perceptions[str(other)].addAcceptance()
            
            if other.current_session == None:
                self.community.createSession(self, other)
                return True
                
            else:
                for participant in other.current_session.participants:
                    if str(self) not in participant.contacts:
                        self.met_through_others += 1
                        participant.met_through_others += 1
                other.current_session.addParticipant(self)
                return True
                
        elif self.proc('sensitivity'):
            self.perceptions[str(other)].addRejection()
            return False
            
        else:
            self.perceptions[str(other)].addUnavailable()
            return False
        
    def getInfo(self, traits=False, memory=False, perceptions=False, friends=False):
        lines = list()
        lines.append("unique ID: %s" % self.sentibyte_ID)
        lines.append("name: %s" % self.name)
        lines.append("acquired knowledge: %d" % len(self.knowledge))
        lines.append("learned from others: %d" % self.learned_from_others)
        lines.append("learned on own: %d" % self.learned_on_own)
        lines.append("others met: %d" % len(self.contacts))
        lines.append("others met through mutual contacts: %d" % self.met_through_others)
        lines.append("invitations to strangers: %d" % self.invitaitons_to_strangers)
        lines.append("invitations to contacts: %d" % self.invitations_to_contacts)
        lines.append("invitations to friends: %d" % self.invitations_to_friends)
        lines.append("current session: %s" % self.current_session)
        
        if traits:   
            #update
            lines.append("personal traits...")
            for trait in self.p_traits:
                lines.append("\t%s: %f (%f base)" % (
                            trait, self[trait]['current'], self[trait]['base']))
            lines.append("interpersonal traits...")
            for trait in self.i_traits:
                lines.append("\t%s: %f (%f base)" % (
                            trait, self[trait]['current'], self[trait]['base']))
            lines.append("desired traits...")
            for trait in self.d_traits:
                lines.append("\t%s: %f (%d priority weight)" % (
                            trait, self.getDesired(trait), self.desire_priority[trait]))
            
        if len(self.friend_list) > 0 and friends:
            lines.append("friends:")
            for friend in self.friend_list:
                perception = self.perceptions[friend]
                
                regard_range = perception.owner['regard']['upper'] - perception.owner['regard']['lower']
                delta_to_min = perception.rating - perception.owner['regard']['lower']
                relative_rating = (delta_to_min / regard_range) * 99
                lines.append("\t%s perception of %s: %f (%f relative)" % (perception.owner, perception.perceived, perception.rating, relative_rating))
                lines.append("\t(%d entries, %d cycles, %d broadcasts)" % (perception.entries, perception.cycles_present, perception.broadcasts))
                lines.append("\t%s has sent %d invitations to %s)" % (perception.perceived, perception.invitations, perception.owner))
                lines.append("\t%s has sent %d invitations to %s)" % (perception.owner, perception.contacts['total'], perception.perceived))
                for key in perception.contacts:
                    lines.append("\t\t%s: %d" % (key, perception.contacts[key]))
            
            for key in perception.p_traits:
                desired = perception.owner.d_traits[key]['base']
                actual = perception.perceived.i_traits[key]['base']
                priority = perception.owner.desire_priority[key]
                lines.append("\t\t%s: %f (%f desired) (%f actual) (%d priority weight)" % (key, perception.p_traits[key], desired, actual, priority))
            
            entry_list = [i.entries for i in self.perceptions.values()]
            lines.append("\taverage entries for connections: %f" % (sum(entry_list) / float(len(entry_list))))
                
            rating_list = [self.getRating(i, relative=True) for i in self.perceptions]
            lines.append("\taverage rating for connections: %f" % (sum(rating_list) / float(len(rating_list))))
        
        return lines
        
    def printTraits(self):
        print "personal traits..."
        for trait in self.p_traits:
            print "\t%s: %f (%f base)" % (trait, self[trait]['current'], self[trait]['base'])
        print "interpersonal traits..."
        for trait in self.i_traits:
            print "\t%s: %f (%f base)" % (trait, self[trait]['current'], self[trait]['base'])
        print "desired traits..."
        for trait in self.d_traits:
            print "\t%s: %f" % (trait, self.getDesired(trait)), 
            priority = self.desire_priority[trait]
            print " (%d priority weight)" % priority
        
    def printConnections(self):
        print '-' * 10
        for sb_ID in self.perceptions:
            print "connection %d..." % i
            self.perceptions[sb_ID].printInfo()
            