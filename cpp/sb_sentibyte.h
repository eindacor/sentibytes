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

	const bool inContacts(string other_ID) const { return stringInVector(other_ID, contacts); }
	const bool inFamily(string other_ID) const { return stringInVector(other_ID, family); }
	const bool inChildren(string other_ID) const { return stringInVector(other_ID, children); }
	const bool inFriends(string other_ID) const { return stringInVector(other_ID, friends); }
	const bool inBonds(string other_ID) const { return std::find(bonds.begin(), bonds.end(), other_ID) == bonds.end(); }
	const bool wouldBond(string other_ID) const;
	const bool inDeparted(string other_ID) const { return stringInVector(other_ID, departed); }

	void addContact(string other_ID);
	void setFriends(vec_str f_list) { friends = f_list; }
	void addFamily(string other_ID) { family.push_back(other_ID); }
	void addChild(string other_ID) { children.push_back(other_ID); }
	void addMemory(const interaction &toAdd);
	void incrementBond(string other_ID);
	void decrementBond(string other_ID);
	void departContact(string other_ID);
	void update(population &community, sentibyte &sb);
	void addInteraction(const interaction &observed, sentibyte &sb);

	const vec_str getFamily() const { return family; }
	const vec_str getChildren() const { return children; }
	const map<string, int> getBonds() const { return bonds; }
	const vec_str getContacts() const { return contacts; }
	const vec_str getFriends() const { return friends; }
	const vec_str getDeparted() const { return friends; }

	const float getRating(string other_ID) const { return perceptions.at(other_ID).getOverallRating(); }
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

class sentibyte
{
public:
	sentibyte(string &name, const map<string, valueState> &p_traits, const map<string, valueState> &i_traits, const map<string, valueState> &d_traits);
	~sentibyte(){};

	const valueState operator [] (string trait) const;
	const bool operator == (const sentibyte &other) const { return sentibyte_ID == other.getID(); }
	const bool operator != (const sentibyte &other) const { return sentibyte_ID != other.getID(); }

	const float getDeathCoefficient() const { return death_coefficient; }
	const signed short getAge() const { return age; }
	const string getID() const { return sentibyte_ID; }
	operator string() const { return sentibyte_ID; }
	const bool proc(string trait) const { return (*this)[trait].proc(); }
	const vec_str getStrangers() const;
	transmission broadcast(const vec_str &target_list) const;
	void interpretTransmission(const transmission &sent);
	const bool proposeBond(string other_ID);
	const bool checkHealth();
	const bool inviteOthers();
	const bool wantsToConnect(string other_ID) const;
	void reflect();
	void learn();
	void fluctuateTraits();
	void updateCycle();
	void sessionCycle();
	void aloneCycle();
	const contacts_ptr readContacts() const { return contacts; }
	contacts_ptr getContacts() { return contacts; }

	// transmission functions cannot be const, because the trait guesses of 
	// each are determined only when 
	void observeTransmission(const transmission &sent);
	void receiveTransmission(const transmission &sent);
	void updateContacts();
	void newInteraction(string other_ID);
	void endInteraction(string other_ID);

	const bool hasInFamily(string other_ID) const { return contacts->inFamily(other_ID); }
	const bool hasInContacts(string other_ID) const { return contacts->inContacts(other_ID); }
	const bool hasInChildren(string other_ID) const { return contacts->inChildren(other_ID); }

private:
	signed short age;
	string name;
	string sentibyte_ID;
	signed short location;
	string current_session_ID;

	session_ptr current_session;
	population_ptr community;
	contacts_ptr contacts;

	signed short cycles_in_current_session;
	signed short cycles_in_session;
	signed short cycles_alone;
	map<string, interaction> current_interactions;
	//first int is line, second int is error index
	//if the error index is -1, that knowledge is accurate
	map<unsigned short, unsigned short> knowledge;
	int social_cooldown;
	float death_coefficient;

	map<string, valueState> p_traits;
	map<string, valueState> d_traits;
	map<string, valueState> i_traits;
	//string is trait, int is multiplier
	map<string, int> desire_priorities;
};

#endif