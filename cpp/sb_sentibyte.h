#ifndef SB_SENTIBYTE_H
#define SB_SENTIBYTE_H

#include "sb_header.h"
#include "sb_communication.h"
#include "sb_perception.h"

class contactManager
{
public:
	contactManager(){};
	~contactManager(){};

	const bool inContacts(string other_ID) const;
	const bool inFamily(string other_ID) const;
	const bool inChildren(string other_ID) const;

	void addContact(string other_ID);
	void setFriends(vector<string> f_list) { friends = f_list; }
	void addFamily(string other_ID) { family.push_back(other_ID); }
	void addChild(string other_ID) { children.push_back(other_ID); }
	void incrementBond(string other_ID);
	void decrementBond(string other_ID);

	const vector<string> getFamily() const { return family; }
	const vector<string> getChildren() const { return children; }
	const map<string, int> getBonds() const { return bonds; }
	const vector<string> getContacts() const { return contacts; }
	const vector<string> getFriends() const { return friends; }

private:
	vector<string> family;
	vector<string> children;
	//int refers to number of rounds in bond list
	map<string, int> bonds;
	vector<string> contacts;
	vector<string> friends;
	community *current_community;
};

class sentibyte
{
public:
	sentibyte(string &name, const map<string, valueState> &p_traits, const map<string, valueState> &i_traits, const map<string, valueState> &d_traits);
	~sentibyte(){};

	const valueState operator [] (string trait) const;
	const bool operator == (const sentibyte &other) const { return sentibyte_ID == other.getID(); }
	const bool operator != (const sentibyte &other) const { return sentibyte_ID != other.getID(); }

	const string getID() const { return sentibyte_ID; }
	operator string() const { return sentibyte_ID; }
	const bool proc(string trait) const { return (*this)[trait].proc(); }
	const float getRating(string other_ID) const { return perceptions.at(other_ID).getOverallRating(); }
	const vector<string> getStrangers() const;
	void broadcast(vector<string> target_list) const;

	// transmission functions cannot be const, because the trait guesses of 
	// each are determined only when 
	void observeTransmission(const transmission &sent);
	void receiveTransmission(const transmission &sent);
	void updateContacts();
	void newInteraction(string other_ID);
	void endInteraction(string other_ID);
	void addMemory(const interaction &toAdd);
	perception_iterator verifyPerception(string other_ID);

	const bool hasInFamily(string other_ID) const { return contacts.inFamily(other_ID); }
	const bool hasInContacts(string other_ID) const { return contacts.inContacts(other_ID); }
	const bool hasInChildren(string other_ID) const { return contacts.inChildren(other_ID); }

private:
	int age;
	string name;
	string sentibyte_ID;
	signed int location;
	memory_map memory;
	perception_map perceptions;
	string current_session_ID;
	session* current_session;
	community* current_community;
	signed short cycles_in_current_session;
	map<string, interaction> current_interactions;
	//first int is line, second int is error index
	//if the error index is -1, that knowledge is accurate
	map<unsigned short, unsigned short> knowledge;
	int social_cooldown;
	contactManager contacts;
	float death_coefficient;

	map<string, valueState> p_traits;
	map<string, valueState> d_traits;
	map<string, valueState> i_traits;
	//string is trait, int is multiplier
	map<string, int> desire_priorities;
};

#endif