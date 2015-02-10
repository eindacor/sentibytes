#ifndef SB_CONNECTIONS_H
#define SB_CONNECTIONS_H

#include "sb_header.h"

class perception
{
public:
	perception(string other, const sentibyte &owner_sb);
	~perception(){};

	const float getOverallRating() const { return overall_rating.getAverage(); }

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

	avg_container overall_rating;
};

class contact_manager
{
public:
	contact_manager(){};
	~contact_manager(){};

	const bool inContacts(string other_ID) const { return stringInVector(other_ID, contacts); }

	void addMemory(const interaction &toAdd);

	const interaction_ptr getRandomMemory() const;
	const interaction_ptr getRandomMemory(string other_ID) const;
	const vector<float> readMemory(string other_ID) const { return memory.at(other_ID); }
	perception_ptr getPerception(string other_ID) { return perceptions.at(other_ID); }

	void departContact(string other_ID);
	void update(population &community, sentibyte &sb);

	const vec_str getContacts() const { return contacts; }
	const signed short getContactCount() const { return contacts.size(); }

	const string_listman_ptr getContactLists() const { return contact_lists; }

	const float getRating(string other_ID) const { return perceptions.at(other_ID)->getOverallRating(); }
	perception_iterator verifyPerception(string other_ID, sentibyte &sb);

private:
	vec_str contacts;
	perception_map perceptions;
	map<string, vector<float> > memory;
	string_listman_ptr contact_lists;
};

#endif