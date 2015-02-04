#include "sb_sentibyte.h"

void contactManager::addContact(string other_ID)
{
	if (std::find(contacts.begin(), contacts.end(), other_ID) == contacts.end())
		contacts.push_back(other_ID);
}

const bool contactManager::inContacts(string other_ID) const
{
	return (std::find(contacts.begin(), contacts.end(), other_ID) == contacts.end());
}

void contactManager::incrementBond(string other_ID)
{
	if (bonds.find(other_ID) == bonds.end())
		bonds[other_ID] = 0;

	bonds[other_ID]++;
}

void contactManager::decrementBond(string other_ID)
{
	if (bonds.find(other_ID) == bonds.end())
		return;

	else if (bonds[other_ID] == 0)
		bonds.erase[other_ID];

	else bonds[other_ID]--;
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
			map<signed short, signed short>::iterator knowledge_it = knowledge.find(index);
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
			perceptions[other_ID].addInteraction(received.getGossip(), *this, true);
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
	updateContacts();
}

void sentibyte::addMemory(const interaction &toAdd)
{

}

void sentibyte::endInteraction(string other_ID)
{
	interaction *interaction_p = &current_interactions[other_ID];
	if (cycles_in_current_session > 0)
	{
		interaction_p->guessTraits(cycles_in_current_session, COMMUNICATIONS_PER_CYCLE);
		perceptions[other_ID].addInteraction(*interaction_p, *this, false);
		updateContacts();

		memory[other_ID].push_back(*interaction_p);
	}

	// code needed to limit number of memories with min heap system

	current_interactions.erase(other_ID);
}

void sentibyte::updateContacts()
{
	vector<perception> perception_list;
	vector<string> contact_list = contacts.getContacts();

	// perception_list in this function is the basis for forming friend list and 
	// potential bonds, so it doesn't include family members
	for (vector<string>::iterator it = contact_list.begin(); it != contact_list.end(); it++)
	{
		if (!hasInFamily(*it))
			perception_list.push_back(perceptions[*it]);
	}

	std::sort(perception_list.begin(), perception_list.end());

	signed short friend_overflow = perception_list.size() - MAX_FRIENDS;

	if (friend_overflow < 0)
		friend_overflow = 0;

	vector<string> friend_list;
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