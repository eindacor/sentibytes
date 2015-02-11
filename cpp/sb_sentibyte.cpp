#include "sb_sentibyte.h"

sentibyte::sentibyte(string name, population* pop)
{
	string ID;

	for (int i = 0; i < 12; i++)
	{
		char c = 'a';
		c += rand() % 26;
		ID += c;
	}

	sentibyte_ID = ID;
	location = rand() % 12;

	community = population_ptr(pop);	
	contacts = contacts_ptr(new contact_manager);

	community->addMember(sentibyte_ID);
}

const list<string> sentibyte::getStrangers() const
{
	list<string> strangers;

	if (community == NULL)
		return strangers;

	for (list<string>::const_iterator it = community->getMembers().begin(); it != community->getMembers().end(); it++)
		if (!contacts->inContacts(*it))
			strangers.push_back(*it);

	return strangers;
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