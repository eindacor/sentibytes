from random import randint, choice, shuffle, random
from jep_loot.jeploot import catRoll
from sb_utilities import getCoefficient, calcInfluence, calcAccuracy, \
    boundsCheck, valueState, randomIndex, listAverage
from sb_fileman import getTruth, getPath, getListOfFiles, \
    traitsFromFile, traitsFromConfig, writeSB
from sb_perception import perception
from heapq import heappush, heappop
from sb_communication import transmission, interaction
            
class sentibyte(object):
    def __init__(self, name, traits):
        self.user_ID = name
        self.name = randint(0, 1000000)
        self.sentibyte_ID = str(self.user_ID) + '.' + str(self.name)
        self.location = randint(0, 10)
        self.age = 0
        
        self.memory = {} #dict of lists of interaction logs, key = sentibyte_ID
        self.perceptions = {}
        self.current_session_ID = None
        self.current_session = None
        self.family = list()
        self.children = list()
        
        self.community = None
        self.current_interactions = {}
        self.friend_list = list()
        self.contacts = list()
        self.bonds = {}
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
        self.cycles_alone = 0
        self.cycles_in_session = 0
        self.cycles_in_current_session = 0
        self.bonds_denied = 0
        self.bonds_postponed = 0
        self.bonds_confirmed = 0
        self.death_coefficient = .000001
        
        # cooldowns prevent cycles spent in session and along at the same time,
        # and restricts when sb's are allowed to be social
        self.social_cooldown = 20
        
        # personal characteristics
        self.p_traits = traits[0]
        self.i_traits = traits[1]
        self.d_traits = traits[2]
        
        desired_list = list(self.d_traits.keys())
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
                self.updateContacts()
                
            if received.brag != None:
                pass
            
    def newInteraction(self, other_ID):
        if other_ID not in self.perceptions:
            self.perceptions[other_ID] = perception(other_ID, self)
            
        if other_ID not in self.contacts:
            self.contacts.append(other_ID)
            
        toAdd = interaction(str(self), other_ID, self.cycles_in_session)
        self.current_interactions[other_ID] = toAdd
        self.updateContacts()
     
    def endInteraction(self, other_ID):
        target = self.current_interactions[other_ID]
        if self.cycles_in_current_session > 0:
            target.guessTraits(self.cycles_in_current_session, self.community.communications_per_cycle)
            
            # add to perception
            self.perceptions[other_ID].addInteraction(target, self)
            self.updateContacts()
        
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
        
        # probably a way to make this simpler, not pulling all perceptions
        perception_list = [self.perceptions[p] for p in self.contacts if p not in self.family]
    
        perception_list.sort()
        #self.contacts = [p.other_ID for p in perception_list]

        list_length = len(perception_list)
        if len(perception_list) > num_friends:
            perception_list = perception_list[(list_length - num_friends):]
            
        self.friend_list = [p.other_ID for p in perception_list]
        
        if self.age >= self.community.child_age:
            bond_list = [other_ID for other_ID in self.contacts if other_ID not in self.family]
            bond_list = [other_ID for other_ID in bond_list if other_ID not in self.community.children]
            bond_list = [other_ID for other_ID in bond_list if other_ID not in self.community.max_children]
            age_factor = 1.0 - (self.death_coefficient * self.age * 100)
            bond_threshold = age_factor * self['selective']['current']
            bond_list = [other_ID for other_ID in bond_list if self.getRating(other_ID) > bond_threshold]
            
            for other_ID in bond_list:
                if other_ID not in self.bonds:
                    self.bonds[other_ID] = 0
            
            omitted = [other_ID for other_ID in self.bonds if other_ID not in bond_list]
            for other_ID in omitted:
                self.bonds.pop(other_ID, None)
                
    def getStrangers(self):
        stranger_list = [other_ID for other_ID in self.community.members if 
                            other_ID != str(self) and 
                            other_ID not in self.memory and
                            other_ID not in self.community.children]
              
        return stranger_list
        
    def broadcast(self, target_list):
        positivity_current = self['positivity']['current']
        positivity_co = self['positivity']['coefficient']
        positivity = calcAccuracy(positivity_current, positivity_co)
        energy_current = self['energy']['current']
        energy_co = self['energy_range']['coefficient']
        energy = calcAccuracy(energy_current, energy_co)
        knowledge = None
        gossip = None
        brag = None
        if self.proc('talkative'):
            t_type = 'statement'
            
            all_knowledge = self.accurate_knowledge + list(self.false_knowledge.keys())
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
                trait = choice(list(self.p_traits.keys()))
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
            other_ID = choice(list(self.memory.keys()))
            if other_ID not in self.community.members:
                # add negative effect for mourning
                pass
            memory_list = self.memory[other_ID]
            memory = choice(memory_list)
            self.perceptions[other_ID].addInteraction(memory, self, isMemory=True)
            self.updateContacts()
    
    def learn(self):
        all_knowledge = (self.accurate_knowledge + list(self.false_knowledge.keys()))
        
        the_truth = getTruth()
        if self.proc('inquisitive') and len(all_knowledge) != len(the_truth):
            unknown = [i for i in the_truth if i not in all_knowledge]
            index = choice(unknown)
            
        else:
            index = choice(list(the_truth.keys()))
        

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
            
    def wantsToBond(self, other_ID):
        if other_ID not in self.bonds:
            return 'no'
            
        if other_ID in self.bonds and (self.bonds[other_ID] < 50 or self.current_session):
            return 'not now'
            
        elif other_ID in self.bonds and self.bonds[other_ID] >= 50:
            return 'yes'
      
    def proposeBond(self, other_ID):
        other = self.community.getMember(other_ID)
        other_response = other.wantsToBond(str(self))
        child_made = False
        if other_response == 'no':
            self.bonds_denied += 1
            #possibly change rating effect
            self.perceptions[other_ID].addInstance(-10)
            self.updateContacts()
        elif other_response == 'not now':
            self.perceptions[other_ID].addInstance(10)
            self.updateContacts()
            self.bonds_postponed += 1
        elif other_response == 'yes':
            self.perceptions[other_ID].addInstance(10)
            self.updateContacts()
            self.bonds_confirmed += 1
            if other.proc('concupiscent'):
                self.community.addMember(createChild(self, other))
                if len(self.children) >= self.community.child_limit:
                    self.community.max_children.append(str(self))
                if len(other.children) >= self.community.child_limit:
                    other.community.max_children.append(other_ID)
                self.community.children_born += 1
                child_made = True
        else: raise
                
        self.community.deactivateMember(other_ID)
        return child_made
    
    def checkHealth(self):
        if random() < self.death_coefficient * self.age:
            self.community.removeMember(str(self))
            return False
            
        else:
            return True
    
    def updateSelf(self):
        # add emotional effects for deaceased friends/family
        deceased_others = list()
        for other_ID in self.contacts:
            if other_ID not in self.community.members:
                deceased_others.append(other_ID)
                
        for other_ID in deceased_others:
            self.contacts.remove(other_ID)
            '''
            if other_ID in self.children:
                self.children.remove(other_ID)
            if other_ID in self.family:
                self.family.remove(other_ID)
            '''
            if other_ID in self.bonds:
                self.bonds.pop(other_ID, None)
        self.updateContacts()
        
        self.age += 1
        if self.current_session:
            self.cycles_in_session += 1
            self.cycles_in_current_session += 1
        else:
            self.cycles_alone += 1
            
        if self.age == self.community.child_age:
            self.community.children.remove(str(self))
            
        if self.proc('volatility'):
            self.fluctuateTraits()
    
    def sessionCycle(self):
        self.updateSelf()
        session = self.current_session
        if len(session.participants) < session.max_participants and self.proc('sociable'):
            if self.sendInvitation():
                self.successful_connection_attempts += 1
            else:
                self.failed_connection_attempts += 1
                
        # submit transmissions
        available_targets = session.getAllOthers(str(self))
        transmission_list = list()
        for i in range(self.community.communications_per_cycle):
            if self.proc('communicative'):
                transmission_list.append(self.broadcast(available_targets))
                
        session.distributeTransmissions(str(self), transmission_list)        
        # proc stamina/leave
        if len(session.new_members) == 0:
            if not self.proc('stamina'):
                session.leaving_list.append(str(self))
                
        if not self.checkHealth():
            return
     
    def aloneCycle(self):
        if not self.checkHealth():
            return
        self.updateSelf()
            
        if self.proc('intellectual'):
            self.learn()

        if self.proc('reflective'):
            self.reflect()		
        
        for other_ID in self.bonds:
            self.bonds[other_ID] += 1
        
        if str(self) not in self.community.max_children and str(self) not in self.community.children:
            if self.proc('concupiscent'):
                potential_bonds = [other_ID for other_ID in self.bonds if self.wantsToBond(other_ID) == 'yes']
                if len(potential_bonds) == 0:
                    return
                
                shuffle(potential_bonds)
                for other_ID in potential_bonds:
                    if self.proposeBond(other_ID):
                        return
                    
        if self.social_cooldown == 0:
            if self.proc('sociable'):
                if self.sendInvitation():
                    self.successful_connection_attempts += 1
                else:
                    self.failed_connection_attempts += 1
        else:
            self.social_cooldown -= 1
    '''      
    def invitationCycle(self):
        if self.social_cooldown == 0:
            if self.proc('sociable'):
                if self.sendInvitation():
                    self.successful_connection_attempts += 1
                else:
                    self.failed_connection_attempts += 1
                    
        else:
            self.social_cooldown -= 1
    '''
    
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
            return self['regard']['current']
            
        return self.perceptions[other_ID].overall_rating.average

    # must be separate from "contact" function to filter out potential contact attempts
    # not just for denying invitations, also for determining who to invite
    def wantsToConnect(self, other_ID):
        inverse_tolerance_coefficient = 1.0 - self['tolerance']['coefficient']
        minimum_rating = 100 * inverse_tolerance_coefficient
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
        self.social_cooldown = 10
      
    # returns true if a session is successfully joined or created
    def connect(self, other_ID):
        self_status = self.community.getAvailability(str(self))
        other_status = self.community.getAvailability(other_ID)
        
        other = self.community.getMember(other_ID)
        
        if other.social_cooldown > 0 or not other.wantsToConnect(str(self)):
            self.community.deactivateMember(other_ID)
            return False
            
        elif other.proc('sociable'):
            if self_status == 'alone' and other_status == 'alone':
                max_participants = 2
                while self.proc('sociable') or other.proc('sociable'):
                    max_participants += 2
                    if max_participants == 24:
                        break
                self.community.createSession(self.sentibyte_ID, other_ID, max_participants)
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
        lines.append("age: %d" % self.age)
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
                            trait, self.d_traits[trait]['current'], self.desire_priority[trait]))
  
        if len(self.friend_list) > 0 and friends:
            lines.append("friends:")
            for friend_ID in self.friend_list:
                friend = self.community.getMember(friend_ID)
                perception = self.perceptions[friend_ID]
                rating = perception.overall_rating.average
                cycles_observed = perception.cycles_observed
                broadcasts_observed = perception.broadcasts_observed
                interaction_count = perception.interaction_count
                memories = perception.memories_counted
                rumors = perception.rumors_heard
                lines.append("\t%s rating of %s: %f" % (self, friend_ID, rating))
                lines.append("\t(%d interactions, %d cycles, %d broadcasts, %d rumors, %d memories)" % \
                    (interaction_count, cycles_observed, broadcasts_observed, rumors, memories))
                
                for trait in self.d_traits:
                    actual_trait = friend[trait]['base']
                    lines.append("\t\t%s: actual = %f, desired = %f, priority = %d" % \
                        (trait, actual_trait, self.d_traits[trait]['base'], self.desire_priority[trait]))
                    
                lines.append("\t\tdesire offset: %f" % self.perceptions[friend_ID].avg_desired_offset.average)
                    
                self.community.deactivateMember(friend_ID)
        
        interaction_count_list = [p.interaction_count for p in self.perceptions.values()]
        if interaction_count_list:
            lines.append("\taverage entries for connections: %f" % listAverage(interaction_count_list))
            
        rating_list = [p.overall_rating.average for p in self.perceptions.values()]
        if rating_list:
            lines.append("\taverage rating for perceptions: %f" % listAverage(rating_list))
        
        return lines
        
def loadPremadeSBs(the_truth):
    premade_sentibytes = list()
    # create sentibytes from files in sb_files directory
    sb_file_path = getPath() + '/sb_files'
    
    files_present = getListOfFiles(sb_file_path)
    
    for file_name in files_present:
        full_path = getPath() + '/sb_files/' + file_name
        traits = traitsFromFile(full_path)
        premade_sentibytes.append(sentibyte(file_name, traits))
        
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
        if i % int(4946 / quantity) == 0:
            name = line.replace('\n', '')
            traits = traitsFromConfig(config_file)
            random_sentibytes.append(sentibyte(name, traits))
            member_counter += 1
            
        if member_counter == quantity:
            break
        
    namefile.close()
    
    for sb in random_sentibytes:
        writeSB(sb)
    
    return [str(sb) for sb in random_sentibytes]

def mergeTraits(sb1_traits, sb2_traits):
    new_traits = {}
    for trait in sb1_traits:
        if random() < .5:
            parent_traits = sb1_traits
        else:
            parent_traits = sb2_traits
        
        parent_lower = 0.0
        parent_base = 50.0
        parent_upper = 100.0
        
        valid_range = False   
        while not valid_range:
            parent_lower = calcAccuracy(parent_traits[trait]['lower'], 1.0, 5)
            parent_base = calcAccuracy(parent_traits[trait]['base'], 1.0, 5)
            parent_upper = calcAccuracy(parent_traits[trait]['upper'], 1.0, 5)
            
            valid_range = parent_lower < parent_base and parent_base < parent_upper
            
        temp_vs = parent_traits[trait].duplicate()
        temp_vs.params['lower'] = parent_lower
        temp_vs.params['base'] = parent_base
        temp_vs.params['current'] = parent_base
        temp_vs.params['upper'] = parent_upper
        temp_vs.update()
    
        new_traits[trait] = temp_vs
        
    return new_traits
    
def createChild(sb1, sb2):
    p_traits = mergeTraits(sb1.p_traits, sb2.p_traits)
    i_traits = mergeTraits(sb1.i_traits, sb2.i_traits)
    d_traits = mergeTraits(sb1.d_traits, sb2.d_traits)
    traits = [p_traits, i_traits, d_traits]
    
    name = ''
    namefile = open(getPath() + '/names.txt')
    index = randint(0, 4946)
    for i, line in enumerate(namefile):
        if i % index == 0 and i != 0:
            name = line.replace('\n', '')
            break
    
    sentibaby = sentibyte(name, traits)
    sentibaby.family = sb1.family + sb2.family
    sb1.family.append(str(sentibaby))
    sb1.children.append(str(sentibaby))
    sb2.family.append(str(sentibaby))
    sb2.children.append(str(sentibaby))
    sentibaby.family.append(str(sb1))
    sentibaby.family.append(str(sb2))
    writeSB(sentibaby)
    
    print ("a sentibaby, %s, is born to %s and %s" % (sentibaby, sb1, sb2))
    return sentibaby.sentibyte_ID

        
        
            
