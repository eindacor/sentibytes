#include "sb_utilities.h"

const float avg_container::combineAverages
(float previous_avg, int previous_count, float added_avg, int added_count) const
{
	if (added_count < 1){
		string error_string = "combineAverages cannot operate with a count less than 1";
		throw error_string;
	}
	int new_count = previous_count + added_count;
	float new_total = (previous_avg * float(previous_count)) + (added_avg * float(added_count));
	return float(new_total / float(new_count));
}

void value_state::fluctuate()
{

}

float boundsCheck(float f)
{
	if (f > 100)
		return 100.0;

	else if (f < 0)
		return 0.0;

	else return f;
}

float calcAccuracy(float target_value, float range_coefficient, float max_offset=10.0)
{
	float random_float = float(rand() % 101) / 100.0f;
	float margain = max_offset * range_coefficient * random_float;
	if (rand() % 2 == 0)
		margain *= -1;
	float new_value = boundsCheck(target_value + margain);
	return new_value;
}

template <typename t>
const vector<t>::const_iterator randomVectorIterator(const vector<t> &vec)
{
	if (vec.size() == 0)
		return vec.end();

	int random_index = rand() % vec.size();
	vector<t>::const_iterator it = vec.begin() + random_interaction_index;
	return it;
}

template <typename t1, typename t2>
const map<t1, t2>::const_iterator randomMapIterator(const map<t1, t2> &m)
{
	if (m.size() == 0)
		return m.end();

	int random_index = rand() % m.size();
	map<t1, t2>::const_iterator it = m.cbegin();
	for (int i = 0; i < random_index; i++)
		it++;

	return it;
}

template<typename t>
void removeFromVector(vector<t> &vec, t target)
{
	vector<t>::iterator it = std::find(vec.begin(), vec.end(), target);
	if (it != vec.end())
		vec.erase(it);
}

template<typename t1, typename t2>
void removeFromMap(map<t1, t2> &m, t1 target)
{
	map<t1, t2>::iterator it = std::find(m.begin(), m.end(), target);
	if (it != m.end())
		m.erase(it);
}

const bool stringInVector(string s, const vec_str &vec)
{
	return std::find(vec.begin(), vec.end(), s) != vec.end();
}