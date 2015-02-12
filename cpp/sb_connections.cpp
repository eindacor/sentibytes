#include "sb_connections.h"

void contact_manager::addMemory(string other_ID, float toAdd)
{
	memory[other_ID].push_back(toAdd);

	if (memory[other_ID].size() > MAX_MEMORIES)
	{
		std::sort(memory[other_ID].begin(), memory[other_ID].end());
		memory[other_ID].erase(memory[other_ID].begin());
	}
}

const pair<string, float> contact_manager::getRandomMemory() const
{
	pair<string, float> null_memory("DEFAULT", -1.0f);

	if (memory.size() == 0)
		return null_memory;

	pair<string, vector<float> > random_memory = randomMapElement<string, vector<float>>(memory);
	vector<float> memory_list = random_memory.second;
	string other_ID = random_memory.first;
	if (memory_list.size() == 0)
		return null_memory;
	float random_value = randomVectorElement<float>(memory_list);
	return pair<string, float>(other_ID, random_value);
}

const float contact_manager::getRandomMemory(string other_ID) const
{
	if (memory.at(other_ID).size() == 0)
		return -1.0f;

	float random_memory = randomVectorElement<float>(memory.at(other_ID));
	return random_memory;
}