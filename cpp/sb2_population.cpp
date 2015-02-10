#include "sb2_population.h"

void population::addList(string list_name)
{
	if (population_lists.find(list_name) == population_lists.end())
		population_lists[list_name] = list<string>();
}

void population::removeList(string list_name)
{
	population_lists.at(list_name);
	population_lists.erase(list_name);
}

void population::addToList(string sb_ID, string list_name)
{
	population_lists.at(list_name).push_back(sb_ID);
}

void population::removeFromList(string sb_ID, string list_name)
{
	population_lists.at(list_name).remove(sb_ID);
}

const bool population::isInList(string sb_ID, string list_name) const
{
	list<string>::const_iterator it =
		std::find(population_lists.at(list_name).begin(), population_lists.at(list_name).end(), sb_ID);

	return it != population_lists.at(list_name).end();
}