#include "sb_sentibyte.h"
#include "sb_utilities.h"

sentibyte::sentibyte(string &name, const map<string, value_state> &p_traits, 
	const map<string, value_state> &i_traits, const map<string, value_state> &d_traits)
{

}

const value_state sentibyte::operator [] (string trait) const
{
	map<string, value_state>::const_iterator target = p_traits.find(trait);
	if (target != p_traits.end())
		return p_traits.at(trait);

	else target = i_traits.find(trait);
	if (target != i_traits.end())
		return i_traits.at(trait);

	string error_string = "trait does not exist";
	throw error_string;
}

void sentibyte::receiveTransmission(const transmission &received)
{
	if (proc("trusting"))
	{
		if (received.hasFact() && proc("intellectual"))
		{
			signed short index = received.getFact().first;
			signed short error = received.getFact().second;
			map<unsigned short, unsigned short>::iterator knowledge_it = knowledge.find(index);
			bool known = (knowledge_it != knowledge.end());

			if (known && knowledge[index] == error)
				return;

			else if (received.isAccurate())
				knowledge[index] = -1;

			else if (!proc("intelligence"))
				knowledge[index] = error;
		}

		if (received.hasGossip())
		{
			string other_ID = received.getGossip().getOther();
			contacts->verifyPerception(other_ID, *this);
			contacts->getPerception(other_ID)->addInteraction(received.getGossip(), *this, true, false);
			updateContacts();
		}
	}
}

void sentibyte::observeTransmission(const transmission &sent)
{
	string source_ID = sent.getSource();
	interaction other_interaction = current_interactions.at(source_ID);

	if (sent.getType() == STATEMENT || proc("observant"))
		other_interaction.addTransmission(sent);

	if (std::find(sent.getAudience().begin(), sent.getAudience().end(), source_ID) != sent.getAudience().end())
		receiveTransmission(sent);
}

void sentibyte::newInteraction(string other_ID)
{
	contacts->verifyPerception(other_ID, *this);
	interaction toAdd(sentibyte_ID, other_ID, cycles_in_current_session);
	current_interactions[other_ID] = toAdd;
	updateContacts();
}

void sentibyte::endInteraction(string other_ID)
{
	interaction *interaction_p = &current_interactions[other_ID];
	if (cycles_in_current_session > 0)
	{
		interaction_p->guessTraits(cycles_in_current_session, COMMUNICATIONS_PER_CYCLE);
		contacts->getPerception(other_ID)->addInteraction(*interaction_p, *this, false, false);
		updateContacts();
		contacts->addMemory(*interaction_p);
	}

	current_interactions.erase(other_ID);
}

const vec_str sentibyte::getStrangers() const
{
	vec_str strangers;
	vec_str members = community->getMembers();
	for (vec_str::iterator it = members.begin(); it != members.end(); it++)
	{
		string other_ID = *it;
		if (contacts->inContacts(other_ID) || contacts->inFamily(other_ID)
			|| other_ID == sentibyte_ID || community->isChild(other_ID))
			continue;

		else strangers.push_back(other_ID);
	}

	return strangers;
}

transmission sentibyte::broadcast(const vec_str &target_list) const
{
	transmission temp_transmission(sentibyte_ID);

	if (current_session == NULL)
		return temp_transmission;

	float positivity_current = (*this)["positivity"]["current"];
	float positivity_coefficient = (*this)["positivity"]["coefficient"];
	float positivity = calcAccuracy(positivity_current, positivity_coefficient);
	temp_transmission.setPositivity(positivity);

	float energy_current = (*this)["energy"]["current"];
	float energy_coefficient = (*this)["energy"]["coefficient"];
	float energy = calcAccuracy(energy_current, energy_coefficient);
	temp_transmission.setEnergy(energy);

	pair<unsigned short, unsigned short> fact(-1, -1);
	interaction gossip();

	transmission_type t_type = (proc("talkative") ? STATEMENT : SIGNAL);
	temp_transmission.setType(t_type);

	if (t_type == STATEMENT)
	{
		if (proc("intellectual") && knowledge.size() > 0)
		{
			map<unsigned short, unsigned short>::const_iterator it = 
				randomMapIterator<unsigned short, unsigned short>(knowledge);

			temp_transmission.setFact(it->first, it->second);
		}

		if (proc("gossipy"))
		{
			vec_str gossip_targets = contacts->getContactsNotInSession(*current_session);
		
			if (gossip_targets.size() > 0)
			{
				vec_str::const_iterator vector_it = randomVectorIterator<string>(gossip_targets);
				string target_ID = *vector_it;

				interaction_ptr random_interaction = contacts->getRandomMemory(target_ID);
				temp_transmission.setGossip(*random_interaction);
			}
		}
	}

	for (vec_str::const_iterator it = target_list.begin(); it != target_list.end(); it++)
	{
		string other_ID = *it;
		if (proc("sociable") && wantsToConnect(other_ID))
			temp_transmission.addAudience(other_ID);
	}

	// targets are randomly selected by sociable procs above, but if none are chosen, a target
	// must be selected at random
	if (temp_transmission.getAudience().size() == 0)
	{
		vec_str::const_iterator selected_it = randomVectorIterator<string>(target_list);
		temp_transmission.addAudience(*selected_it);
	}

	return temp_transmission;
}

void sentibyte::interpretTransmissions(const vector<transmission> &transmission_list)
{
	for (vector<transmission>::const_iterator it = transmission_list.begin(); it != transmission_list.end(); it++)
	{
		string source_ID = it->getSource();

		if (it->getType() == STATEMENT || proc("observant"))
		{
			current_interactions[source_ID].addTransmission(*it);

			if (stringInVector(sentibyte_ID, it->getAudience()))
				receiveTransmission(*it);
		}
	}
}

void sentibyte::reflect()
{
	interaction_ptr random_memory = contacts->getRandomMemory();
	if (random_memory)
	{
		string other_ID = random_memory->getOther();
		contacts->getPerception(other_ID)->addInteraction(*random_memory, *this, false, true);
	}
}

void sentibyte::learn()
{
	signed short index;
	signed short error = (proc("intelligence") ? -1 : rand() % 12);

	if (proc("inquisitive"))
	{
		vector<signed short> unknown;
		for (int i = 0; i < community->getTruth(); i++)
		{
			if (std::find(knowledge.begin(), knowledge.end(), i) == knowledge.end())
				unknown.push_back(i);
		}

		index = *(randomVectorIterator<signed short>(unknown));
	}
	
	else index = rand() % community->getTruth();

	knowledge[index] = error;
}

void sentibyte::fluctuateTraits()
{
	for (map<string, value_state>::iterator it = p_traits.begin();
		it != p_traits.end(); it++)
		it->second.fluctuate();

	for (map<string, value_state>::iterator it = i_traits.begin();
		it != i_traits.end(); it++)
		it->second.fluctuate();

	for (map<string, value_state>::iterator it = d_traits.begin();
		it != d_traits.end(); it++)
		it->second.fluctuate();
}

const bool sentibyte::proposeBond(string other_ID)
{
	sb_ptr other_p = community->getMember(other_ID);

	string other_response = other_p->getContacts()->wantsToBond(sentibyte_ID);
	bool child_made = false;

	if (other_response == "no")
		contacts->getPerception(other_ID)->addInstance(-10);

	else if (other_response == "not now")
		contacts->getPerception(other_ID)->addInstance(10);

	else if (other_response == "yes")
	{
		contacts->getPerception(other_ID)->addInstance(10);
		if (other_p->proc("concupiscent"))
		{
			community->addMember(createChild(*this, *other_p));
			child_made = true;
		}
	}

	else throw;
	community->deactivateMember(other_ID);
	updateContacts();
	return child_made;
}

void sentibyte::updateAge()
{
	age++;
	signed int death_chance = 10000;
	if (rand() % death_chance == rand() % death_chance)
	{
		if (community != NULL)
			community->removeMember(sentibyte_ID);
	}
}

void sentibyte::sessionCycle()
{
	updateCycle();
	if (current_session->getParticipants().size() < current_session->getLimit() && proc("sociable"))
		inviteOthers();

	vec_str available_targets = current_session->getAllOthers(sentibyte_ID);
	vector<transmission> transmissions;

	for (int i = 0; i < COMMUNICATIONS_PER_CYCLE; i++)
	{
		if (proc("communicative"))
			transmissions.push_back(broadcast(available_targets));
	}

	current_session->distributeTransmissions(transmissions);
	if (current_session->getNewMembers().size() > 0)
	{
		if (!proc("stamina"))
			current_session->addLeaving(sentibyte_ID);
	}

	checkHealth();
}

void sentibyte::aloneCycle()
{
	updateCycle();

	if (!checkHealth())
		return;

	if (proc("intellectual"))
		learn();

	if (age > CHILD_AGE)
	{
		if (proc("reflective"))
			reflect();

		vector<string> potential_bonds(contacts->getBondIDs());
		if (potential_bonds.size() == 0)
			return;

		shuffle(potential_bonds.begin(), potential_bonds.end(), rand());
		for (vector<string>::const_iterator it = potential_bonds.begin(); it != potential_bonds.end(); it++)
			if (proposeBond(*it))
				return;

		if (proc("sociable"))
			inviteOthers();
	}
}

const bool sentibyte::inviteOthers()
{
	updateContacts();
	vector<string> target_list;
	if (contacts->getContactCount() == 0)
		target_list = getStrangers();

	else if (proc("adventurous"))
	{
		//these if statements are separated to prevent calling getStrangers() more than needed
		vector<string> strangers = getStrangers();
		if (strangers.size > 0)
			target_list = strangers;
	}

	else if (proc("pickiness") && contacts->getFriendCount())
		target_list = contacts->getFriends();

	else target_list = contacts->getContacts();

	if (current_session != NULL)
		community->removeIDByAvailability(target_list, IN_OPEN_SESSION, IN_FULL_SESSION);

	else community->removeIDByAvailability(target_list, IN_FULL_SESSION);

	/*  
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
		*/
}

const bool sentibyte::wantsToConnect(string other_ID) const
{

}

const string createChild(sentibyte &sb1, sentibyte &sb2)
{
	//add to max children if maxed out
}