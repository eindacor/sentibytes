#ifndef SB_CONNECTIONS_H
#define SB_CONNECTIONS_H

#include "sb_header.h"

class perception
{
public:
	perception(string other, const sentibyte &owner_sb);
	~perception(){};

	const float getOverallRating() const { return overall_rating.getAverage(); }
	const float getDesiredOffset() const { return avg_desired_offset.getAverage(); }
	const float getInteractionRating() const { return avg_interaction_rating.getAverage(); }
	const float getInstanceRating() const { return avg_instance_rating.getAverage(); }

	void addInteraction(interaction observed, sentibyte &sb, bool isRumor, bool isMemory);
	void addInstance(unsigned short weight);
	const string getOwner() const { return owner_ID; }
	const string getOther() const { return other_ID; }

	const bool operator == (const perception &comparator) const { return (getOverallRating() == comparator.getOverallRating()); }
	const bool operator != (const perception &comparator) const { return (getOverallRating() != comparator.getOverallRating()); }
	const bool operator < (const perception &comparator) const { return (getOverallRating() < comparator.getOverallRating()); }
	const bool operator <= (const perception &comparator) const { return (getOverallRating() <= comparator.getOverallRating()); }
	const bool operator > (const perception &comparator) const { return (getOverallRating() > comparator.getOverallRating()); }
	const bool operator >= (const perception &comparator) const { return (getOverallRating() >= comparator.getOverallRating()); }

	operator float() const { return getOverallRating(); }

private:
	string owner_ID;
	string other_ID;
	signed short broadcasts_observed;
	signed short cycles_observed;
	signed short rumors_heard;
	signed short memories_counted;

	avg_container overall_rating;
	avg_container avg_desired_offset;
	avg_container avg_interaction_rating;
	avg_container avg_instance_rating;
};

class contactManager
{
public:
	contactManager(){};
	~contactManager(){};

	const bool inContacts(string other_ID) const { return stringInVector(other_ID, contacts); }
	const bool inFamily(string other_ID) const { return stringInVector(other_ID, family); }
	const bool inChildren(string other_ID) const { return stringInVector(other_ID, children); }
	const bool inFriends(string other_ID) const { return stringInVector(other_ID, friends); }
	const bool inBonds(string other_ID) const { return std::find(bonds.begin(), bonds.end(), other_ID) == bonds.end(); }
	const bool wouldBond(string other_ID) const;
	vector<string> getBondIDs() const;
	const bool inDeparted(string other_ID) const { return stringInVector(other_ID, departed); }

	void addContact(string other_ID);
	void setFriends(vec_str f_list) { friends = f_list; }
	void addFamily(string other_ID) { family.push_back(other_ID); }
	void addChild(string other_ID) { children.push_back(other_ID); }
	void addMemory(const interaction &toAdd);
	
	const vector<string> getContactsNotInSession(const session &s) const;
	const interaction_ptr getRandomMemory() const;
	const interaction_ptr getRandomMemory(string other_ID) const;
	const vector<interaction_ptr> readMemory(string other_ID) const { return memory.at(other_ID); }
	perception_ptr getPerception(string other_ID) { return perceptions.at(other_ID); }

	void incrementBond(string other_ID);
	void decrementBond(string other_ID);
	void departContact(string other_ID);
	void update(population &community, sentibyte &sb);

	const vec_str getFamily() const { return family; }
	const vec_str getChildren() const { return children; }
	const map<string, int> getBonds() const { return bonds; }
	const vec_str getContacts() const { return contacts; }
	const vec_str getFriends() const { return friends; }
	const vec_str getDeparted() const { return friends; }
	const signed short getContactCount() const { return contacts.size(); }
	const signed short getFriendCount() const { return friends.size(); }
	const signed short getFamilyCount() const { return family.size(); }
	const signed short getChildrenCount() const { return children.size(); }

	const float getRating(string other_ID) const { return perceptions.at(other_ID)->getOverallRating(); }
	perception_iterator verifyPerception(string other_ID, sentibyte &sb);
	const string wantsToBond(string other_ID);

private:
	vec_str family;
	vec_str children;
	//int refers to number of rounds in bond list
	map<string, int> bonds;
	vec_str contacts;
	vec_str friends;
	vec_str departed;
	perception_map perceptions;
	memory_map memory;
};

#endif