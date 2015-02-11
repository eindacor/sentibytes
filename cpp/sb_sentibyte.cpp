#include "sb_sentibyte.h"

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