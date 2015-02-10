#ifndef SB_POPULATION_H
#define SB_POPULATION_H

#include "sb_header.h"

class population
{
public:
	population(){};
	~population(){};

	const list<string> getMembers() const { return members; }
	void deactivateMember(string sb_ID);
	sb_ptr activateMember(string sb_ID);
	void addMember(string sb_ID) { members.push_back(sb_ID); }
	void removeMember(string sb_ID);

	void addList(string list_name);
	void removeList(string list_name);
	void addToList(string sb_ID, string list_name);
	void removeFromList(string sb_ID, string list_name);
	const bool isInList(string sb_ID, string list_name) const;

private:
	list<string> members;
	vector<sb_ptr> active_members;
	map<string, list<string>> population_lists;
};

#endif