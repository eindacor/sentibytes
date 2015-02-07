#include "sb_header.h"
#include "sb_connections.h"
#include "sb_utilities.h"
#include "sb_sentibyte.h"

perception::perception(string other, const sentibyte &owner_sb)
{
	owner_ID = owner_sb.getID();
	other_ID = other;
	broadcasts_observed = 0;
	cycles_observed = 0;
	rumors_heard = 0;
	memories_counted = 0;

	avgContainer overall_rating(owner_sb["regard"]["current"], 0);
}

void perception::addInteraction(interaction observed, sentibyte &sb, bool isRumor, bool isMemory)
{

}

void perception::addInstance(unsigned short weight)
{
	float rating = boundsCheck(getOverallRating() + float(weight));
	avg_instance_rating.addValue(rating);
	overall_rating.addValue(rating);
}

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

const interaction_ptr contactManager::getRandomMemory() const
{
	if (memory.size() == 0)
		return interaction_ptr(NULL);
	memory_iterator m_it = randomMapIterator<string, vector<interaction_ptr>>(memory);
	if (m_it->second.size() == 0)
		return interaction_ptr(NULL);
	vector<interaction_ptr>::const_iterator v_it = randomVectorIterator<interaction_ptr>(m_it->second);
	return *v_it;
}

const interaction_ptr contactManager::getRandomMemory(string other_ID) const
{
	if (memory.at(other_ID).size() == 0)
		return interaction_ptr(NULL);

	vector<interaction_ptr>::const_iterator v_it = randomVectorIterator<interaction_ptr>(memory.at(other_ID));
	return *v_it;
}

void contactManager::departContact(string other_ID)
{
	departed.push_back(other_ID);
	removeFromVector<string>(contacts, other_ID);
	removeFromVector<string>(friends, other_ID);
	//removeFromVector<string>(family, other_ID);
	//removeFromVector<string>(children, other_ID);
	removeFromMap<string, int>(bonds, other_ID);
}

perception_iterator contactManager::verifyPerception(string other_ID, sentibyte &sb)
{
	perception_iterator perception_it = perceptions.find(other_ID);
	bool new_perception = (perception_it == perceptions.end());

	if (new_perception)
	{
		perception_ptr default_perception(new perception(other_ID, sb));
		perceptions.insert(pair<string, perception_ptr>(other_ID, default_perception));
	}

	perception_it = perceptions.find(other_ID);
	return perception_it;
}

void contactManager::addMemory(const interaction &toAdd)
{
	string other_ID = toAdd.getOther();
	interaction_ptr new_memory(new interaction(toAdd));
	memory[other_ID].push_back(new_memory);

	if (memory[other_ID].size() > MAX_MEMORIES)
	{
		std::sort(memory[other_ID].begin(), memory[other_ID].end());
		memory[other_ID].erase(memory[other_ID].begin());
	}
}

const vector<string> contactManager::getContactsNotInSession(const session &s) const
{
	vector<string> gossip_targets;
	for (memory_iterator it = memory.begin(); it != memory.end(); it++)
	{
		string other_ID = it->first;
		if (!s.hasParticipant(other_ID))
			gossip_targets.push_back(other_ID);
	}

	return gossip_targets;
}

const string contactManager::wantsToBond(string other_ID)
{
	if (inBonds(other_ID))
	{
		if (wouldBond(other_ID))
			return "yes";

		else return "not now";
	}
	else return "no";
}

void contactManager::update(population &community, sentibyte &sb)
{
	vec_str deceased_others;
	// find others that are in contacts but not in members
	for (vec_str::const_iterator it = contacts.begin();
		it != contacts.end(); it++)
	{
		if (!stringInVector(community.getMembers(), *it))
			deceased_others.push_back(*it);
	}

	for (vec_str::const_iterator it = deceased_others.begin(); it != deceased_others.end(); it++)
		departContact(*it);

	vector<perception_ptr> perception_list;

	// perception_list in this function is the basis for forming friend list and 
	// potential bonds, so it doesn't include family members
	for (vec_str::iterator it = contacts.begin(); it != contacts.end(); it++)
	{
		if (!inFamily(*it))
			perception_list.push_back(perceptions[*it]);
	}

	std::sort(perception_list.begin(), perception_list.end());

	signed short friend_overflow = perception_list.size() - MAX_FRIENDS;

	if (friend_overflow < 0)
		friend_overflow = 0;

	friends.clear();
	bool addToFriends = false;
	float age_factor = 1.0 - (sb.getDeathCoefficient() * sb.getAge() * 100);
	float bond_threshold = age_factor * sb["selective"]["current"];
	for (vector<perception_ptr>::iterator it = perception_list.begin(); it != perception_list.end(); it++)
	{
		string other_ID = (*it)->getOther();
		if (it == perception_list.begin() + friend_overflow)
			addToFriends = true;

		if (addToFriends)
			friends.push_back(other_ID);

		if (sb.getAge() > int(CHILD_AGE))
		{
			if (getRating(other_ID) > bond_threshold)
				incrementBond(other_ID);

			else decrementBond(other_ID);
		}
	}
}