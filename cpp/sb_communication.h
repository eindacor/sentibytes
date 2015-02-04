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
	const vector<string> getAudience() const { return audience; }
	const pair<unsigned short, unsigned short> getFact() const { return fact; }
	const interaction getGossip() const { return gossip; }

private:
	string source_ID;
	float positivity;
	float energy;
	transmission_type t_type;
	vector<string> audience;
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

private:
	vector<string> participants;
};

class community
{
public:
	community(){};
	~community(){};

	const vector<string> getMembers() const { return members; }
	const bool isChild(string sb_ID) const;

private:
	vector<string> members;
	vector<string> children;
};

#endif