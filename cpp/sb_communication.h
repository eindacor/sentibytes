#ifndef SB_COMMUNICATION_H
#define SB_COMMUNICATION_H

#include "sb_utilities.h"

class interaction;

class transmission
{
public:
	transmission(string source);
	~transmission(){};
	
	void setPositivity(float f) { positivity = f; }
	void setEnergy(float f) { energy = f; }
	void setType(transmission_type t) { t_type = t; }
	void addAudience(string other_ID) { audience.push_back(other_ID); }
	void setFact(unsigned short index, unsigned short error) { fact.first = index; fact.second = error; }
	void setGossip(const interaction &g) { gossip = g; }

	const bool hasFact() const { return fact.first != -1; }
	const bool isAccurate() const { return (hasFact() && fact.second != -1); }
	const bool hasGossip() const { return gossip.getOwner() != "DEFAULT"; }
	const string getSource() const { return source_ID; }
	const float getPositivity() const { return positivity; }
	const float getEnergy() const { return energy; }
	const transmission_type getType() const { return t_type; }
	const vec_str getAudience() const { return audience; }
	const pair<unsigned short, unsigned short> getFact() const { return fact; }
	const interaction getGossip() const { return gossip; }

private:
	string source_ID;
	float positivity;
	float energy;
	transmission_type t_type;
	vec_str audience;
	pair<unsigned short, unsigned short> fact;
	interaction gossip;
};

class interaction
{
public:
	interaction::interaction();
	interaction(string owner, string other, signed short start_cycle);
	~interaction(){};

	const bool isValid() const { return cycles_present > 0; }
	const string getOwner() const { return owner_ID; }
	const string getOther() const { return other_ID; }
	const map<string, float> getGuesses() const { return trait_guesses; }
	const signed int getCyclesPresent() const { return cycles_present; }
	const signed int getCount() const { return transmission_count; }

	const float getPositivity() const { return avg_positivity.getAverage(); }
	const float getEnergy() const { return avg_energy.getAverage(); }
	const float getFacts() const { return avg_facts.getAverage(); }
	const float getGossip() const { return avg_gossip.getAverage(); }

	const bool operator == (const interaction &other) const { return cycles_present == other.getCyclesPresent(); }
	const bool operator != (const interaction &other) const { return cycles_present != other.getCyclesPresent(); }
	const bool operator >= (const interaction &other) const { return cycles_present >= other.getCyclesPresent(); }
	const bool operator <= (const interaction &other) const { return cycles_present <= other.getCyclesPresent(); }
	const bool operator > (const interaction &other) const { return cycles_present > other.getCyclesPresent(); }
	const bool operator < (const interaction &other) const { return cycles_present < other.getCyclesPresent(); }

	void operator = (const interaction &other);

	void addTransmission(const transmission &received);
	void guessTraits(signed short cycles_in_ession, signed short communications_per_cycle);

private:
	string owner_ID;
	string other_ID;
	map<string, float> trait_guesses;
	signed short start_cycle;
	signed short cycles_present;
	avgContainer avg_positivity;
	avgContainer avg_energy;
	avgContainer avg_facts;
	avgContainer avg_gossip;
	signed int transmission_count;
	signed int statement_count;
};

class session
{
public:
	session(){};
	~session(){};

	const bool hasParticipant(string sb_ID) const { return std::find(participants.begin(), participants.end(), sb_ID) == participants.end(); }
	const vec_str getParticipants() const { return participants; }
	const signed short getLimit() const { return participant_limit; }
	const vec_str getAllOthers(string sb_ID) const;
	void distributeTransmissions(const vector<transmission> &transmissions) const;
	const vec_str getNewMembers() const { return new_members; }
	void addLeaving(string sb_ID);

private:
	vec_str participants;
	signed short participant_limit;
	vec_str new_members;
};

class population
{
public:
	population(){};
	~population(){};

	const vec_str getMembers() const { return members; }
	const bool isChild(string sb_ID) const { return stringInVector(sb_ID, children); }
	unsigned short getTruth() const { return the_truth; }
	void deactivateMember(string sb_ID);
	void addMember(string sb_ID) { members.push_back(sb_ID); children.push_back(sb_ID); }
	void addMaxChildren(string sb_ID) { max_children.push_back(sb_ID); }
	void removeChild(string sb_ID);
	void removeMember(string sb_ID);
	sb_ptr getMember(string sb_ID);
	const sb_status getAvailability(string sb_ID) const;
	void removeIDByAvailability(vector<string> &vec, sb_status status, ...);

private:
	vec_str members;
	vec_str children;
	vec_str max_children;
	vec_str in_session;
	vector<sb_ptr> active_members;
	unsigned short the_truth;
};

#endif