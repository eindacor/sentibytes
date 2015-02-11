#ifndef SB_SENTIBYTE_H
#define SB_SENTIBYTE_H

#include "sb_header.h"
#include "sb_connections.h"
#include "sb_population.h"

class sentibyte
{
public:
	sentibyte(string name, population* pop);
	~sentibyte(){};

	operator string() const { return sentibyte_ID; }
	const value_state operator [] (string trait) const { return traits.at(trait); }
	const bool operator == (const sentibyte &other) const { return sentibyte_ID == other.getID(); }
	const bool operator != (const sentibyte &other) const { return sentibyte_ID != other.getID(); }

	const string getID() const { return sentibyte_ID; }
	const list<string> getStrangers() const;
	contacts_ptr getContacts() { return contacts; }
	string_listman_ptr getContactLists() { return contacts->getContactLists(); }

	const vector<string> getTopContacts() { return contacts->getTop(MAX_FRIENDS); }

	const bool traitExists(string trait_name) const { return traits.find(trait_name) == traits.end(); }
	const bool proc(string trait) const { return traits.at(trait).proc(); }

	void fluctuateTraits();
	void setID(string id) { sentibyte_ID = id; }

	const vector<string> getFavorite(int n) { return contacts->getTop(n); }

	void addTrait(string trait_name, const value_state &vs);

private:
	string sentibyte_ID;
	signed short location;

	population_ptr community;
	contacts_ptr contacts;

	map<string, value_state> traits;
};

sentibyte createChild(const sentibyte &mother, const sentibyte &father);

#endif