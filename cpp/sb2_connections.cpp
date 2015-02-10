#include "sb2_connections.h"

void contactManager::addContactList(string list_name)
{
	if (contact_lists.find(list_name) == contact_lists.end())
		contact_lists[list_name] = list<string>();
}

void contactManager::removeContactList(string list_name)
{
	contact_lists.at(list_name);
	contact_lists.erase(list_name);
}

void contactManager::addToContactList(string sb_ID, string list_name)
{
	contact_lists.at(list_name).push_back(sb_ID);
}

void contactManager::removeFromContactList(string sb_ID, string list_name)
{
	contact_lists.at(list_name).remove(sb_ID);
}

const bool contactManager::isInContactList(string sb_ID, string list_name) const
{
	list<string>::const_iterator it =
		std::find(contact_lists.at(list_name).begin(), contact_lists.at(list_name).end(), sb_ID);

	return it != contact_lists.at(list_name).end();
}