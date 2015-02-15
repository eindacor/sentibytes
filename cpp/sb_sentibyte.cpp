#include "sb_sentibyte.h"

const list<string> sentibyte::getStrangers() const
{
	list<string> strangers;

	if (community == NULL)
		return strangers;

	list<string> members = community->getMembers();
	for (list<string>::const_iterator it = members.begin(); it != members.end(); it++)
		if (!contacts->inContacts(*it) && *it != sentibyte_ID)
			strangers.push_back(*it);

	return strangers;
}

void sentibyte::addToContactList(string to_add, string list_name)
{
	if (!contacts->inContacts(to_add))
		contacts->addContact(to_add);
	contacts->getContactLists()->addToList(to_add, list_name);
}

void sentibyte::removeFromContactList(string to_remove, string list_name)
{
	contacts->getContactLists()->removeFromList(to_remove, list_name);
}

void sentibyte::removeFromContacts(string to_remove)
{
	contacts->removeContact(to_remove);
}

void sentibyte::fluctuateTraits()
{
	for (map<string, value_state>::iterator it = traits.begin(); it != traits.end(); it++)
		it->second.fluctuate();
}

void sentibyte::addTrait(string trait_name, const value_state &vs)
{
	try
	{
		traits.at(trait_name);
		throw "trait to add already exists";
	}

	catch (std::out_of_range oor)
	{
		traits[trait_name] = vs;
		return;
	}

	catch (string s)
	{
		cout << s << endl;
	}
}