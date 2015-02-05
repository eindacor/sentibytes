#include "sb_sentibyte.h"
#include "sb_utilities.h"

void contactManager::decrementBond(string other_ID)
{
	if (bonds.find(other_ID) == bonds.end())
		return;

	else if (bonds[other_ID] == 0)
		bonds.erase[other_ID];

	else bonds[other_ID]--;
}

const bool contactManager::wouldBond(string other_ID) const
{
	if (!inBonds(other_ID))
		return false;

	else return (bonds.at(other_ID) >= BOND_POINT ? true : false);
}

sentibyte::sentibyte(string &name, const map<string, valueState> &p_traits, 
	const map<string, valueState> &i_traits, const map<string, valueState> &d_traits)
{

}

const valueState sentibyte::operator [] (string trait) const
{
	map<string, valueState>::const_iterator target = p_traits.find(trait);
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
			verifyPerception(other_ID);
			perceptions[other_ID].addInteraction(received.getGossip(), *this, true, false);
			//updateContacts();
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

perception_iterator sentibyte::verifyPerception(string other_ID)
{
	perception_iterator perception_it = perceptions.find(other_ID);
	bool new_perception = (perception_it == perceptions.end());

	if (new_perception)
	{
		perception default_perception(other_ID, *this);
		perceptions.insert(pair<string, perception>(other_ID, default_perception));
	}

	perception_it = perceptions.find(other_ID);
	return perception_it;
}

void sentibyte::newInteraction(string other_ID)
{
	verifyPerception(other_ID);
	interaction toAdd(sentibyte_ID, other_ID, cycles_in_current_session);
	current_interactions[other_ID] = toAdd;
	//updateContacts();
}

void sentibyte::addMemory(const interaction &toAdd)
{
	string other_ID = toAdd.getOther();
	memory[other_ID].push_back(toAdd);

	if (memory[other_ID].size() > MAX_MEMORIES)
	{
		std::sort(memory[other_ID].begin(), memory[other_ID].end());
		memory[other_ID].erase(memory[other_ID].begin());
	}
}

void sentibyte::endInteraction(string other_ID)
{
	interaction *interaction_p = &current_interactions[other_ID];
	if (cycles_in_current_session > 0)
	{
		interaction_p->guessTraits(cycles_in_current_session, COMMUNICATIONS_PER_CYCLE);
		perceptions[other_ID].addInteraction(*interaction_p, *this, false, false);
		//updateContacts();

		addMemory(*interaction_p);
	}

	current_interactions.erase(other_ID);
}

void sentibyte::updateContacts()
{
	vector<perception> perception_list;
	vec_str contact_list = contacts.getContacts();

	// perception_list in this function is the basis for forming friend list and 
	// potential bonds, so it doesn't include family members
	for (vec_str::iterator it = contact_list.begin(); it != contact_list.end(); it++)
	{
		if (!hasInFamily(*it))
			perception_list.push_back(perceptions[*it]);
	}

	std::sort(perception_list.begin(), perception_list.end());

	signed short friend_overflow = perception_list.size() - MAX_FRIENDS;

	if (friend_overflow < 0)
		friend_overflow = 0;

	vec_str friend_list;
	map<string, int> bond_list = contacts.getBonds();
	bool addToFriends = false;
	float age_factor = 1.0 - (death_coefficient * age * 100);
	float bond_threshold = age_factor * (*this)["selective"]["current"];
	for (vector<perception>::iterator it = perception_list.begin(); it != perception_list.end(); it++)
	{
		string other_ID = (*it).getOther();
		if (it == perception_list.begin() + friend_overflow)
			addToFriends = true;

		if (addToFriends)
			friend_list.push_back(other_ID);

		if (age > int(CHILD_AGE))
		{
			if (getRating(other_ID) > bond_threshold)
				contacts.incrementBond(other_ID);

			else contacts.decrementBond(other_ID);
		}		
	}

	contacts.setFriends(friend_list);		
}

const vec_str sentibyte::getStrangers() const
{
	vec_str strangers;
	vec_str members = community->getMembers();
	for (vec_str::iterator it = members.begin(); it != members.end(); it++)
	{
		string other_ID = *it;
		if (contacts.inContacts(other_ID) || contacts.inFamily(other_ID)
			|| other_ID == sentibyte_ID || community->isChild(other_ID))
			continue;

		else strangers.push_back(other_ID);
	}

	return strangers;
}

transmission sentibyte::broadcast(const vec_str &target_list) const
{
	transmission temp_transmission(sentibyte_ID);

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
			vec_str gossip_targets;
			for (memory_iterator it = memory.begin(); it != memory.end(); it++)
			{
				string other_ID = it->first;
				if (!current_session->hasParticipant(other_ID))
					gossip_targets.push_back(other_ID);
			}

			if (gossip_targets.size() > 0)
			{
				vec_str::const_iterator vector_it = randomVectorIterator<string>(gossip_targets);
				string target_ID = *vector_it;

				// selects a random index between 0 and # of interactions for that ID
				vector<interaction>::const_iterator interaction_it = randomVectorIterator<interaction>(memory.at(target_ID));
				temp_transmission.setGossip(*interaction_it);
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

void sentibyte::interpretTransmission(const transmission &sent)
{
	string source_ID = sent.getSource();
	
	if (sent.getType() == STATEMENT || proc("observant"))
	{
		current_interactions[source_ID].addTransmission(sent);

		if (stringInVector(sentibyte_ID, sent.getAudience()))
			receiveTransmission(sent);
	}
}

void sentibyte::reflect()
{
	if (memory.size() > 0)
	{
		memory_iterator memory_it = randomMapIterator<string, vector<interaction>>(memory);
		vector<interaction>::const_iterator interaction_it = randomVectorIterator<interaction>(*memory_it);
		string other_ID = interaction_it->getOther();
		perceptions[other_ID].addInteraction(*interaction_it, *this, false, true);
		//updateContacts();
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
	for (map<string, valueState>::iterator it = p_traits.begin();
		it != p_traits.end(); it++)
		it->second.fluctuate();

	for (map<string, valueState>::iterator it = i_traits.begin();
		it != i_traits.end(); it++)
		it->second.fluctuate();

	for (map<string, valueState>::iterator it = d_traits.begin();
		it != d_traits.end(); it++)
		it->second.fluctuate();
}

const string sentibyte::wantsToBond(string other_ID) const
{
	if (contacts.inBonds(other_ID))
	{
		if (contacts.wouldBond(other_ID))
			return "yes";

		else return "not now";
	}

	else return "no";
}

const bool sentibyte::proposeBond(string other_ID)
{
	sentibyte *other_p = community->getMember(other_ID);
	sentibyte other = *other_p;

	string other_response = other.wantsToBond(sentibyte_ID);
	bool child_made = false;

	if (other_response == "no")
	{
		perceptions[other_ID].addInstance(-10);
		//updateContacts();
	}

	else if (other_response == "not now")
	{
		perceptions[other_ID].addInstance(10);
		//updateContacts();
	}

	else if (other_response == "yes")
	{
		perceptions[other_ID].addInstance(10);
		//updateContacts();
		if (other.proc("concupiscent"))
		{
			community->addMember(createChild(*this, other));
			child_made = true;
		}
	}

	else throw;

	community->deactivateMember(other_ID);
	return child_made;
}

const bool sentibyte::checkHealth()
{
	signed int death_chance = 10000;
	if (rand() % death_chance == rand() % death_chance)
	{
		community->removeMember(sentibyte_ID);
		return false;
	}

	else return true;
}

void sentibyte::updateSelf()
{
	vec_str deceased_others;
	// find others that are in contacts but not in members
	for (vec_str::const_iterator it = contacts.getContacts().begin();
		it != contacts.getContacts().end(); it++)
	{
		if (!stringInVector(community->getMembers(), *it))
			deceased_others.push_back(*it);
	}

	for (vec_str::const_iterator it = deceased_others.begin(); it != deceased_others.end(); it++)
		contacts.departContact(*it);

	updateContacts();

	age++;
	if (current_session != NULL)
	{
		cycles_in_current_session++;
		cycles_in_session++;
	}

	else cycles_alone++;

	if (age == CHILD_AGE)
		community->removeChild(sentibyte_ID);

	if (proc("volatility"))
		fluctuateTraits();
}

void sentibyte::sessionCycle()
{
	updateSelf();
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
	updateSelf();

	if (!checkHealth())
		return;

	if (proc("intellectual"))
		learn();

	if (proc("reflective"))
		reflect();


}

const bool sentibyte::wantsToConnect(string other_ID) const
{

}

const string createChild(sentibyte &sb1, sentibyte &sb2)
{
	//add to max children if maxed out
}