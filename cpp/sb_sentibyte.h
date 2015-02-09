#ifndef SB_SENTIBYTE_H
#define SB_SENTIBYTE_H

#include "sb_header.h"
#include "sb_communication.h"
#include "sb_connections.h"

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
	const vec_str getStrangers() const;
	contacts_ptr getContacts() { return contacts; }

	operator string() const { return sentibyte_ID; }

	const bool hasInFamily(string other_ID) const { return contacts->inFamily(other_ID); }
	const bool hasInContacts(string other_ID) const { return contacts->inContacts(other_ID); }
	const bool hasInChildren(string other_ID) const { return contacts->inChildren(other_ID); }

	const bool proc(string trait) const { return (*this)[trait].proc(); }	

	void interpretTransmissions(const vector<transmission> &transmission_list);
	void seekBond();
	void reflect();
	void learn();
	void fluctuateTraits();
	void updateAge();
	void getTransmissions();
	transmission broadcast(const vec_str &target_list) const;

	const bool proposeBond(string other_ID);
	const bool checkHealth();
	const bool inviteOthers();
	const bool wantsToConnect(string other_ID) const;
	
	void updateCycle();
	void sessionCycle();
	void aloneCycle();

	// transmission functions cannot be const, because the trait guesses of 
	// each are determined only when 
	void observeTransmission(const transmission &sent);
	void receiveTransmission(const transmission &sent);
	void updateContacts();
	void newInteraction(string other_ID);
	void endInteraction(string other_ID);

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