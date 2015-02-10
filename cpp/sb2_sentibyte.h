#ifndef SB_SENTIBYTE_H
#define SB_SENTIBYTE_H

#include "sb_header.h"
#include "sb_communication.h"
#include "sb_connections.h"

class sentibyte
{
public:
	sentibyte(string name, const map<string, value_state> &added_traits);
	sentibyte(string name);
	~sentibyte(){};

	operator string() const { return sentibyte_ID; }
	const value_state operator [] (string trait) const;
	const bool operator == (const sentibyte &other) const { return sentibyte_ID == other.getID(); }
	const bool operator != (const sentibyte &other) const { return sentibyte_ID != other.getID(); }

	const string getID() const { return sentibyte_ID; }
	const vec_str getStrangers() const;
	contacts_ptr getContacts() { return contacts; }

	const bool hasInFamily(string other_ID) const { return contacts->inFamily(other_ID); }
	const bool hasInContacts(string other_ID) const { return contacts->inContacts(other_ID); }
	const bool hasInChildren(string other_ID) const { return contacts->inChildren(other_ID); }
	const bool traitExists(string trait_name) const { return std::find(traits.begin(), traits.end(), trait_name) == traits.end(); }
	const bool proc(string trait) const { return (*this)[trait].proc(); }

	void reflect();
	void learn();
	void fluctuateTraits();
	void setID(string id) { sentibyte_ID = id; }

	const vector<string> getFavorite(int n);

	void addTrait(string trait_name, const value_state &vs);

	// transmission functions cannot be const, because the trait guesses of 
	// each are determined only when 
	void updateContacts();

private:
	string sentibyte_ID;
	signed short location;

	population_ptr community;
	contacts_ptr contacts;

	map<string, value_state> traits;
};

#endif