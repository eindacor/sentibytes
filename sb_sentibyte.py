from random import randrange, randint, choice, uniform, shuffle
from jep_loot.jeploot import catRoll
from sb_utilities import getCoefficient, calcInfluence, calcAccuracy, \
    boundsCheck, valueState, randomIndex, listAverage
from sb_fileman import getTruth, getPath, getListOfFiles, \
    traitsFromFile, traitsFromConfig, writeSB
from sb_perception import perception
from heapq import heappush, heappop
from sb_communication import transmission, interaction
            
class sentibyte(object):
    def __init__(self, name, the_truth, traits):
        self.user_ID = name
        self.name = randint(0, 1000000)
        self.location = randint(0, 10)
        
        self.sentibyte_ID = str(self.user_ID) + '.' + str(self.name)
        
        self.memory = {} #dict of lists of interaction logs, key = sentibyte_ID
        self.perceptions = {}
        self.current_session_ID = None
        self.current_session = None
        
        self.community = None
        self.current_interactions = {}
        self.friend_list = list()
        self.contacts = list()
        self.accurate_knowledge = list()
        self.false_knowledge = {}
        
        self.learned_on_own = 0
        self.learned_from_others = 0
        self.misled_by_others = 0
        self.corrected_by_others = 0
        self.met_through_others = 0
        self.met_on_own = 0
        self.invitations_to_friends = 0
        self.invitations_to_contacts = 0
        self.invitations_to_strangers = 0
        self.failed_connection_attempts = 0
        self.successful_connection_attempts = 0
        self.successful_connections_friends = 0
        self.successful_connections_contacts = 0
        self.successful_connections_strangers = 0
        self.unsuccessful_connections_friends = 0
        self.unsuccessful_connections_contacts = 0
        self.unsuccessful_connections_strangers = 0
        self.rejection_count = 0
        self.accepted_count = 0
        self.sociable_count = 0
        self.cycles_alone = 0
        self.cycles_in_session = 0
        self.cycles_in_current_session = 0
        
        # cooldowns prevent cycles spent in session and along at the same time,
        # and restricts when sb's are allowed to be social
        self.social_cooldown = 0
        
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
      
    # this function analyzes transmissions even if self was not one of the targets
    # for better accuracty of guessing traits
    def interpretTransmission(self, sent):
        source = sent.source_ID
        
        # add modifiers for interpretation
        if sent.t_type == 'statement' or self.proc('observant'):
            self.current_interactions[source].addTransmission(sent)
            
            if str(self) in sent.targets:
                self.receiveTransmission(sent)
                
    def receiveTransmission(self, received):
        # transmissions no longer have effect on others' positivity and energy
        # self['positivity'].influence(received.positivity)
        # self['energy'].influence(received.energy)
        
        # add perception effects for agreements/disagreements
        if self.proc('trusting'):
            if received.knowledge != None and self.proc('intellectual'):
                info_index = received.knowledge[0]
                
                # if the information given is false
                if len(received.knowledge) > 1:
                    if self.proc('intelligence'):
                        return
                    
                    elif info_index in self.accurate_knowledge:
                        self.accurate_knowledge.remove(info_index)
                    
                    self.false_knowledge[info_index] = received.knowledge[1]
                    self.misled_by_others += 1
                
                elif info_index in self.false_knowledge:
                    del self.false_knowledge[info_index]
                    self.corrected_by_others += 1
                
                if info_index not in self.accurate_knowledge:
                    self.accurate_knowledge.append(info_index)
                    
                self.learned_from_others += 1
                
            if received.gossip != None:
                other_ID = received.gossip.other_ID
                if other_ID not in self.perceptions:
                    self.perceptions[other_ID] = perception(other_ID, self)
                    
                self.perceptions[other_ID].addInteraction(received.gossip, self, isRumor=True)
                
            if received.brag != None:
                pass
            
    def newInteraction(self, other_ID):
        if other_ID not in self.perceptions:
            self.perceptions[other_ID] = perception(other_ID, self)
            
        if other_ID not in self.contacts:
            self.contacts.append(other_ID)
            
        toAdd = interaction(str(self), other_ID)
        
        self.current_interactions[other_ID] = toAdd
     
    def endInteraction(self, other_ID):
        target = self.current_interactions[other_ID]
        target.guessTraits(self.cycles_in_current_session, self.community.communications_per_cycle)
        
        # add to perception
        self.perceptions[other_ID].addInteraction(target, self)
        
        # add to memory
        if other_ID not in self.memory:
            self.memory[other_ID] = list()
            
        heappush(self.memory[other_ID], self.current_interactions[other_ID])
        
        if len(self.memory[other_ID]) > 8:
            heappop(self.memory[other_ID])
        
        # remove from interactions
        self.current_interactions.pop(other_ID, None)
        
    def updateContacts(self):
        num_friends = 12
        
        perception_list = [self.perceptions[p] for p in self.contacts]
    
        perception_list.sort()
        self.contacts = [p.other_ID for p in perception_list]

        list_length = len(perception_list)
        if len(perception_list) > num_friends:
            perception_list = perception_list[(list_length - num_friends):]
            
        self.friend_list = [p.other_ID for p in perception_list]
    
    def getStrangers(self):
        stranger_list = [other_ID for other_ID in self.community.members 
                        if other_ID != self.sentibyte_ID and other_ID not in self.memory]
              
        return stranger_list
        
    def broadcast(self, target_list):
        positivity_current = self.getCurrent('positivity')
        positivity_co = self.getCoefficient('positivity')
        positivity = calcAccuracy(positivity_current, positivity_co)
        energy_current = self.getCurrent('energy')
        energy_co = self.getCoefficient('energy_range')
        energy = calcAccuracy(energy_current, energy_co)
        knowledge = None
        gossip = None
        brag = None
        if self.proc('talkative'):
            t_type = 'statement'
            
            all_knowledge = self.accurate_knowledge + self.false_knowledge.keys()
            if self.proc('intellectual') and len(all_knowledge) > 0:
                knowledge = list()
                index = choice(all_knowledge)
                knowledge.append(index)
                if index in self.false_knowledge:
                    knowledge.append(self.false_knowledge[index])
            
            # if gossipy procs, sb sends an interaction memory as a broadcast
            gossip_targets = [other_ID for other_ID in self.memory.keys() if other_ID not in self.current_session.participants]   
            if len(gossip_targets) > 0 and self.proc('gossipy'):     
                other_ID = choice(gossip_targets)
                memory_list = self.memory[other_ID]
                gossip = choice(memory_list)
                    
            if self.proc('confident'):
                brag = {}
                trait = choice(self.p_traits.keys())
                brag[trait] = self[trait]['current']
      
        else:
            t_type = 'signal'
            
        # add preference for talking to different people
        selected_targets = list()
        
        while self.proc('sociable'):
            for other_ID in target_list:
                if self.wantsToConnect(other_ID) and other_ID not in selected_targets:
                    selected_targets.append(other_ID)
            
        if len(selected_targets) == 0:
            selected_targets.append(choice(target_list))
            
        toSend = transmission(self.sentibyte_ID, selected_targets, positivity, 
                        energy, t_type, knowledge=knowledge, gossip=gossip, brag=brag)
        return toSend
        
    def reflect(self):
        # add modifier for positivity
        if len(self.memory) > 0:
            other_ID = choice(self.memory.keys())
            memory_list = self.memory[other_ID]
            memory = choice(memory_list)
            self.perceptions[other_ID].addInteraction(memory, self, isMemory=True)
    
    def learn(self):
        all_knowledge = (self.accurate_knowledge + self.false_knowledge.keys())
        
        the_truth = getTruth()
        if self.proc('inquisitive') and len(all_knowledge) != len(the_truth):
            unknown = [i for i in the_truth if i not in all_knowledge]
            index = choice(unknown)
            
        else:
            index = choice(the_truth.keys())
        

        if self.proc('intelligence'):
            if index in self.false_knowledge:
                del self.false_knowledge[index]
            
            if index not in self.accurate_knowledge:    
                self.accurate_knowledge.append(index)
            
        else:
            if index in self.accurate_knowledge:
                self.accurate_knowledge.remove(index)
                
            self.false_knowledge[index] = randomIndex(the_truth[index])
        
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
        self.cycles_alone += 1
        if str(self) not in self.community.recently_left_session:
            if self.proc('volatility'):
                self.fluctuateTraits()
                
            elif self.proc('intellectual'):
                self.learn()
    
            if self.proc('reflective'):
                self.reflect()			
                
    def invitationCycle(self):
        if self.proc('sociable'):
            self.sociable_count += 1
            if self.sendInvitation():
                self.successful_connection_attempts += 1
            else:
                self.failed_connection_attempts += 1
    
    # Seeks other sentibytes for communication, returns true if a connection is 
    # made, false if not
    def sendInvitation(self):
        self.updateContacts()
        # generate list of targets (strangers, contacts, or friends)
        if len(self.contacts) == 0:
            selected_type = 'strangers'
            target_list = self.getStrangers()
            
        elif self.proc('adventurous') and len(self.getStrangers()) != 0:
            selected_type = 'strangers'
            target_list = self.getStrangers()
            self.invitations_to_strangers += 1
            
        elif self.proc('pickiness') and len(self.friend_list) != 0:
            selected_type = 'friends'
            target_list = self.friend_list[:]
            self.invitations_to_friends += 1
        
        else:
            selected_type = 'contacts'
            target_list = self.contacts[:]
            self.invitations_to_contacts += 1
        
        # if self in session, invite someone sb that is alone
        # update to give sb's opportunity to switch session
        if self.current_session:
            target_list = [sb_ID for sb_ID in target_list if self.community.getAvailability(sb_ID) == 'alone']
        else:
            target_list = [sb_ID for sb_ID in target_list if self.community.getAvailability(sb_ID) == 'in open session' \
                            or self.community.getAvailability(sb_ID) == 'alone']
            
        target_list = [sb_ID for sb_ID in target_list if self.wantsToConnect(sb_ID)]
        
        weighed_options = {}
        for other_ID in target_list:
            if other_ID in self.perceptions:
                weighed_options[other_ID] = self.getRating(other_ID)
            else:
                weighed_options[other_ID] = self['regard']['current']
            
        if len(weighed_options) == 0:
            return self.logConnection(False, selected_type)
            
        selected_ID = catRoll(weighed_options)
        
        # keep contacting until there are no targets left or a connection is made
        while self.connect(selected_ID) == False:
            del weighed_options[selected_ID]
            
            if len(weighed_options) == 0:
                return self.logConnection(False, selected_type)
         
            selected_ID = catRoll(weighed_options)
            
        return self.logConnection(True, selected_type)
        
    def logConnection(self, successful, target):
        if target == 'strangers':
            if successful:
                self.successful_connections_strangers += 1
                return True

            else:
                self.unsuccessful_connections_strangers += 1
                return False

        if target == 'contacts':
            if successful:
                self.successful_connections_contacts += 1
                return True

            else:
                self.unsuccessful_connections_contacts += 1
                return False

        if target == 'friends':
            if successful:
                self.successful_connections_friends += 1
                return True

            else:
                self.unsuccessful_connections_friends += 1
                return False
        
    # returns rating of particular sentibyte by ID or object
    # if the target is yet to make contact with self, returns self's current
    # regard level
    def getRating(self, other_ID):
        if other_ID not in self.perceptions:
            default_perception = perception('default', self)
            return default_perception.rating
            
        return self.perceptions[other_ID].rating

    # must be separate from "contact" function to filter out potential contact attempts
    # not just for denying invitations, also for determining who to invite
    def wantsToConnect(self, other_ID):
        inverse_tolerance_coefficient = 1.0 - self['tolerance']['coefficient']
        minimum_rating = 99 * inverse_tolerance_coefficient
        accepted = self.getRating(other_ID) >= minimum_rating
        if not accepted:
            self.rejection_count += 1
            
        else:
            self.accepted_count += 1
        return accepted
    
    def joinSession(self, session):
        self.current_session_ID = session.session_ID
        self.current_session = session
        
    def leaveSession(self):
        self.current_session_ID = None
        self.current_session = None
        self.cycles_in_current_session = 0
      
    # returns true if a session is successfully joined or created
    def connect(self, other_ID):
        self_status = self.community.getAvailability(str(self))
        other_status = self.community.getAvailability(other_ID)
        
        other = self.community.getMember(other_ID)
        
        if not other.wantsToConnect(str(self)):
            self.community.deactivateMember(other_ID)
            return False
            
        elif other.proc('sociable'):
            if self_status == 'alone' and other_status == 'alone':
                self.community.createSession(self.sentibyte_ID, other_ID)
                return True
                
            elif self_status == 'in open session' and other_status == 'alone':
                self.current_session.addParticipant(other_ID, inviter_ID=str(self))
                return True
                
            elif self_status == 'alone' and other_status == 'in open session':
                other.current_session.addParticipant(str(self), inviter_ID=str(other))
                return True
            
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
        lines.append("successful connections to strangers: %d" % self.successful_connections_strangers)
        lines.append("successful connections to contacts: %d" % self.successful_connections_contacts)
        lines.append("successful connections to friends: %d" % self.successful_connections_friends)
        lines.append("unsuccessful connections to strangers: %d" % self.unsuccessful_connections_strangers)
        lines.append("unsuccessful connections to contacts: %d" % self.unsuccessful_connections_contacts)
        lines.append("unsuccessful connections to friends: %d" % self.unsuccessful_connections_friends)
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
            for friend_ID in self.friend_list:
                friend = self.community.getMember(friend_ID)
                perception = self.perceptions[friend_ID]
                rating = perception.rating
                cycles_observed = perception.cycles_observed
                broadcasts_observed = perception.broadcasts_observed
                interaction_count = perception.interaction_count
                memories = perception.memories_counted
                rumors = perception.rumors_heard
                lines.append("\t%s rating of %s: %f" % (self, friend_ID, rating))
                lines.append("\t(%d interactions, %d cycles, %d broadcasts, %d rumors, %d memories)" % \
                    (interaction_count, cycles_observed, broadcasts_observed, rumors, memories))
                
                for trait in self.d_traits:
                    perceived_trait = self.perceptions[friend_ID].perceived_traits[trait]
                    actual_trait = friend[trait]['base']
                    lines.append("\t\t%s: %f (actual: %f, desired: %f)" % \
                        (trait, perceived_trait, actual_trait, self.d_traits[trait]['base']))
                    
                lines.append("\t\tperception offset: %f" % self.perceptions[friend_ID].getAveragePerceivedOffset(friend))
                lines.append("\t\tdesire offset: %f" % self.perceptions[friend_ID].getAverageDesiredOffset(self))
                    
                self.community.deactivateMember(friend_ID)
        
        interaction_count_list = [p.interaction_count for p in self.perceptions.values()]
        if interaction_count_list:
            lines.append("\taverage entries for connections: %f" % listAverage(interaction_count_list))
            
        rating_list = [p.rating for p in self.perceptions.values()]
        if rating_list:
            lines.append("\taverage rating for connections: %f" % listAverage(rating_list))
        
        return lines
        
def loadPremadeSBs(the_truth):
    premade_sentibytes = list()
    # create sentibytes from files in sb_files directory
    sb_file_path = getPath() + '/sb_files'
    
    files_present = getListOfFiles(sb_file_path)
    
    for file_name in files_present:
        full_path = getPath() + '/sb_files/' + file_name
        traits = traitsFromFile(full_path)
        premade_sentibytes.append(sentibyte(file_name, the_truth, traits))
        
    for sb in premade_sentibytes:
        writeSB(sb)
        
    return [str(sb) for sb in premade_sentibytes]
  
# generates a random number of sentibytes using names from the names.txt file  
def createRandomSBs(quantity, the_truth):
    config_file = getPath() + '/traits_config.txt'
    
    random_sentibytes = list()
    
    member_counter = 0
    namefile = open(getPath() + '/names.txt')
    for i, line in enumerate(namefile):
        if i % (4946 / quantity) == 0:
            name = line.replace('\n', '')
            traits = traitsFromConfig(config_file)
            random_sentibytes.append(sentibyte(name, the_truth, traits))
            member_counter += 1
            
        if member_counter == quantity:
            break
        
    namefile.close()
    
    for sb in random_sentibytes:
        writeSB(sb)
    
    return [str(sb) for sb in random_sentibytes]
        
            
