#include "sb_communication.h"
#include "sb_utilities.h"


transmission::transmission(string source) : source_ID(source), fact(-1, -1)
{
	positivity = -1;
	energy = -1;
	t_type = NO_T_TYPE;
}

void interaction::addTransmission(const transmission &received)
{
	if (received.getSource() == owner_ID)
	{
		string error_string = "cannot add owner's transmissions to his/her own interaction";
		throw error_string;
	}

	avg_positivity.addValue(received.getPositivity());
	avg_energy.addValue(received.getEnergy());
	pair<unsigned short, unsigned short> fact = received.getFact();
	if (received.hasFact())
		avg_facts.addValue(1);
	else if (received.getType() == STATEMENT)
		avg_facts.addValue(0);

	//if the gossip has been instantiated, add to average
	if (received.hasGossip())
		avg_gossip.addValue(1);
	else if (received.getType() == STATEMENT)
		avg_gossip.addValue(0);

	transmission_count++;

	if (received.getType() == STATEMENT)
		statement_count++;
}

void interaction::guessTraits(signed short cycles_in_session, signed short communications_per_cycle)
{
	cycles_present = cycles_in_session - start_cycle;
	map<string, float>::const_iterator toFind;

	if (cycles_present > 0 && communications_per_cycle > 0)
	{
		//Communicative
		float communicative_guess = transmission_count / float(cycles_present * communications_per_cycle);
		communicative_guess = boundsCheck(communicative_guess * 100);
		toFind = trait_guesses.find("communicative");
		if (toFind != trait_guesses.end())
			trait_guesses["communicative"] = communicative_guess;
		else trait_guesses.insert(pair<string, float>("communicative", communicative_guess));

		//Talkative
		float talkative_guess = float(statement_count / transmission_count);
		talkative_guess = boundsCheck(talkative_guess * 100);
		toFind = trait_guesses.find("talkative");
		if (toFind != trait_guesses.end())
			trait_guesses["talkative"] = talkative_guess;
		else trait_guesses.insert(pair<string, float>("talkative", talkative_guess));
	}

	if (transmission_count > 0)
	{
		//Intellectual
		float intellectual_guess = avg_facts.getAverage();
		toFind = trait_guesses.find("intellectual");
		if (toFind != trait_guesses.end())
			trait_guesses["intellectual"] = intellectual_guess;
		else trait_guesses.insert(pair<string, float>("intellectual", intellectual_guess));

		//Gossipy
		float gossipy_guess = avg_gossip.getAverage();
		toFind = trait_guesses.find("gossipy");
		if (toFind != trait_guesses.end())
			trait_guesses["gossipy"] = gossipy_guess;
		else trait_guesses.insert(pair<string, float>("gossipy", gossipy_guess));

		//Positivity
		float positivity_guess = avg_positivity.getAverage();
		if (toFind != trait_guesses.end())
			trait_guesses["positivity"] = positivity_guess;
		else trait_guesses.insert(pair<string, float>("positivity", positivity_guess));

		//Energy
		float energy_guess = avg_energy.getAverage();
		if (toFind != trait_guesses.end())
			trait_guesses["energy"] = energy_guess;
		else trait_guesses.insert(pair<string, float>("energy", energy_guess));
	}
}