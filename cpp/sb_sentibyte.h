#ifndef SB_SENTIBYTE_H
#define SB_SENTIBYTE_H

#include "sb_header.h"
#include "sb_connections.h"
#include "sb_population.h"

class sentibyte
{
public:
	sentibyte(string name, population_ptr pop) : contacts(new contact_manager), location(rand() % 13) { community = pop; sentibyte_ID = generateID(name); }
	~sentibyte(){};

	operator string() const { return sentibyte_ID; }
	const value_state operator [] (string trait) const { return traits.at(trait); }
	const bool operator == (const sentibyte &other) const { return sentibyte_ID == other.getID(); }
	const bool operator != (const sentibyte &other) const { return sentibyte_ID != other.getID(); }

	const string getID() const { return sentibyte_ID; }
	const list<string> getStrangers() const;
	void addContactList(string list_name) { contacts->getContactLists()->addList(list_name); }
	void removeContactList(string list_name) { contacts->getContactLists()->removeList(list_name); }
	//modify addToContactList so that contact_manager adds string to general contacts as well
	void addToContactList(string to_add, string list_name);
	void removeFromContactList(string to_remove, string list_name);
	void removeFromContacts(string to_remove);
	const bool isInContactList(string to_find, string list_name) const{ return contacts->getContactLists()->isInList(to_find, list_name); }
	const list<string> getContacts() const { return contacts->getContacts(); }
	const list<string> getContactList(string list_name) const { return contacts->getContactLists()->getList(list_name); }
	const vector<string> getContactListNames() const { return contacts->getContactListNames(); }

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