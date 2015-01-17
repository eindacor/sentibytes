from random import randrange, randint, choice, uniform, shuffle
import random
from jep_loot.jeploot import catRoll
from sb_communication import session, transmission, interaction
from sb_utilities import getCoefficient, calcInfluence, calcAccuracy, \
    boundsCheck, weightedAverage, valueState, randomIndex
from sb_perception import perception
from heapq import heappush, heappop
            
class sentibyte(object):
    def __init__(self, name, the_truth, traits):
        self.user_ID = name
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
        self.accurate_knowledge = list()
        self.false_knowledge = {}
        self.the_truth = the_truth
        
        self.learned_on_own = 0
        self.learned_from_others = 0
        self.misled_by_others = 0
        self.corrected_by_others = 0
        self.met_through_others = 0
        self.invitations_to_friends = 0
        self.invitations_to_contacts = 0
        self.invitations_to_strangers = 0
        self.failed_connection_attempts = 0
        self.successful_connection_attempts = 0
        self.sociable_count = 0
        self.cycles_alone = 0
        self.cycles_in_session = 0
        
        # cooldowns prevent cycles spent in session and along at the same time,
        # and restricts when sb's are allowed to be social
        self.social_cooldown = 0
        self.cycle_cooldown = 0
        
        # personal characteristics
        self.p_traits = traits[0]
        self.i_traits = traits[1]
        self.d_traits = traits[2]
        
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
            raise Exception("trait (%s) not found" % index)
        
    def __eq__(self, other):
        return self.sentibyte_ID == other.sentibyte_ID
        
    def __ne__(self, other):
        return self.sentibyte_ID != other.sentibyte_ID
        
    def __str__(self):
        return self.sentibyte_ID
        
    # returns true based on trait passed
    def proc(self, trait):
        if trait in self.p_traits:
            return self.p_traits[trait].proc()
            
        elif trait in self.i_traits:
            return self.i_traits[trait].proc()
            
        else:
            raise Exception("trait (%s) not found" % trait)
        
    # returns current value of passed trait    
    def getCurrent(self, trait):
        if trait in self.p_traits:
            return self.p_traits[trait].params['current']
            
        elif trait in self.i_traits:
            return self.i_traits[trait].params['current']

        else:
            raise Exception("trait (%s) not found" % trait)
            
    def getCoefficient(self, trait):
        if trait in self.p_traits:
            return self.p_traits[trait].params['coefficient']
            
        elif trait in self.i_traits:
            return self.i_traits[trait].params['coefficient']

        else:
            raise Exception("trait (%s) not found" % trait)
            
    def getDesired(self, trait):
        return self.d_traits[trait]['current']
            
    def getSession(self):
        return self.current_session
        
    def isAvailable(self):
        return self.current_session == None
            
    def addCommunity(self, new):
        self.community = new
            
    # called from session cycle if stamina trait is not proc'ed
    def removeSession(self):
        self.current_session = None
        self.cycle_cooldown = 1
        # removed after influence no longer changes within session
        #self.i_traits['positivity'].params['current'] = self['positivity']['base'] 
            
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
        
    def updateFriends(self):
        num_friends = 8
        
        perception_list = [self.perceptions[p] for p in self.contacts 
                            if self.perceptions[p].entries > 0]
    
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
        
    def receiveTransmission(self, received):
        # transmissions no longer have effect on others' positivity and energy
        # self['positivity'].influence(received.positivity)
        # self['energy'].influence(received.energy)
        
        # add perception effects for agreements/disagreements
        
        if len(received.information) and self.proc('trusting') and self.proc('intellectual'):
            info_index = received.information[0]
            
            # if the information given is false
            if len(received.information) > 1:
                if self.proc('intelligence'):
                    return
                
                elif info_index in self.accurate_knowledge:
                    self.accurate_knowledge.remove(info_index)
                
                self.false_knowledge[info_index] = received.information[1]
                self.misled_by_others += 1
            
            elif info_index in self.false_knowledge:
                del self.false_knowledge[info_index]
                self.corrected_by_others += 1
            
            if info_index not in self.accurate_knowledge:
                self.accurate_knowledge.append(info_index)
                
            self.learned_from_others += 1
        
    def broadcast(self, targets):
        positivity_current = self.getCurrent('positivity')
        positivity_co = self.getCoefficient('positivity')
        positivity = calcAccuracy(positivity_current, positivity_co)
        energy_current = self.getCurrent('energy')
        energy_co = self.getCoefficient('energy_range')
        energy = calcAccuracy(energy_current, energy_co)
        information = list()
        if self.proc('talkative'):
            t_type = 'statement'
            
            if self.proc('intellectual'):
                all_knowledge = self.accurate_knowledge + self.false_knowledge.keys()
                index = choice(all_knowledge)
                information.append(index)
                
                if index in self.false_knowledge:
                    information.append(self.false_knowledge[index])
        
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
        all_knowledge = (self.accurate_knowledge + self.false_knowledge.keys())
        
        if self.proc('inquisitive') and len(all_knowledge) != len(self.the_truth):
            unknown = [i for i in self.the_truth if i not in all_knowledge]
            index = choice(unknown)
            
        else:
            index = choice(self.the_truth.keys())
        

        if self.proc('intelligence'):
            if index in self.false_knowledge:
                del self.false_knowledge[index]
            
            if index not in self.accurate_knowledge:    
                self.accurate_knowledge.append(index)
            
        else:
            if index in self.accurate_knowledge:
                self.accurate_knowledge.remove(index)
                
            self.false_knowledge[index] = randomIndex(self.the_truth[index])
        
        self.learned_on_own += 1
     
    # cycles through all traits, fluctuating each 
    def fluctuateTraits(self):
        for trait in self.p_traits:
            self.p_traits[trait].fluctuate()
                
        for trait in self.d_traits:
            self.d_traits[trait].fluctuate()
            
        for trait in self.i_traits:
            self.i_traits[trait].fluctuate()
      
    def aloneCycle(self):
        if self.cycle_cooldown == 0:
            self.cycles_alone += 1
            if self.proc('volatility'):
                self.fluctuateTraits()
                
            elif self.proc('intellectual'):
                self.learn()
    
            if self.proc('reflective'):
                self.reflect()			
        
        else:
            self.cycle_cooldown -= 1
        
    def invitationCycle(self):
        if self.social_cooldown == 0:
            if self.proc('sociable'):
                self.sociable_count += 1
                if not self.joinSession():
                    self['positivity'].influence(self['positivity']['lower'])
                    self.failed_connection_attempts += 1
                    
                else:
                    self.successful_connection_attempts += 1
                        
        else:
            self.social_cooldown -= 1
      
    # Seeks other sentibytes for communication, returns true if a connection is 
    # made, false if not
    def joinSession(self):
        self.updateFriends()
        # generate list of targets (strangers, contacts, or friends)
        target_list = list()
        if (self.proc('adventurous') or len(self.friend_list) == 0) and len(self.getStrangers()) != 0:
            target_list = self.getStrangers()
            self.invitations_to_strangers += 1
            
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
        
        # keep contacting until there are no targets left or a connection is made
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
     
    # Returns average distance from percieved trait to actual base value of other
    def getPerceptionOffset(self, other):
        self.addPerception(other)
		
        return self.perceptions[other].getAverageOffset()
    
    # must be separate from "contact" function to filter out potential contact attempts
    # not just for denying invitations, also for determining who to invite
    def wantsToContact(self, other):
        inverse_tolerance = 99 - self['tolerance']['current']
        return self.getRating(str(other), relative=True) >= inverse_tolerance
       
    # returns true if a session is successfully joined or created
    def contact(self, other):
        other.addPerception(self)
        self.addPerception(other)
        other.perceptions[str(self)].addInvitation()
        
        if not other.wantsToContact(self):
            self.perceptions[str(other)].addRejection()
            
        elif type(other.current_session) != type(None) and len(other.current_session.participants) > 24:
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
        lines.append("accurate knowledge: %d" % len(self.accurate_knowledge))
        lines.append("false knowledge: %d" % len(self.false_knowledge))
        lines.append("learned from others: %d" % self.learned_from_others)
        lines.append("learned on own: %d" % self.learned_on_own)
        lines.append("others met: %d" % len(self.contacts))
        lines.append("others met through mutual contacts: %d" % self.met_through_others)
        lines.append("invitations to strangers: %d" % self.invitations_to_strangers)
        lines.append("invitations to contacts: %d" % self.invitations_to_contacts)
        lines.append("invitations to friends: %d" % self.invitations_to_friends)
        lines.append("cycles alone: %s" % self.cycles_alone)
        lines.append("cycles in session: %s" % self.cycles_in_session)
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
            
        entry_list = [i.entries for i in self.perceptions.values()]
        if entry_list:
            lines.append("\taverage entries for connections: %f" % (sum(entry_list) / float(len(entry_list))))
            
        rating_list = [self.getRating(i, relative=True) for i in self.perceptions]
        if rating_list:
            lines.append("\taverage rating for connections: %f" % (sum(rating_list) / float(len(rating_list))))
        
        return lines
        
            
