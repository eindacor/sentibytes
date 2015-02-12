#include "sb_utilities.h"

const float randomFloat(float min, float max, int precision)
{
	double precision_multiplier = pow(10, precision);
	signed int min_int = int(min * precision_multiplier);
	signed int max_int = int(max * precision_multiplier);

	if (max_int <= min_int)
		throw;

	int range = max_int - min_int;
	int random_number = rand() % (range + 1);
	random_number += min_int;
	float random_float = float(random_number) / precision_multiplier;
	return random_float;
}

/*
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
*/

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
	m.erase(it);
}

const bool stringInVector(string s, const vec_str &vec)
{
	return std::find(vec.begin(), vec.end(), s) != vec.end();
}

value_state::value_state()
{
	setBounds(0.0f, 100.0f);
	setBase();
	params[VS_CURRENT] = params[VS_BASE];
	fluctuation_coefficient = randomFloat(.02, .05, 4);
	fluctuation_sensitivity = randomFloat(.02, .2, 4);
	update();
}

value_state::value_state(float lower_bound, float base, float upper_bound)
{
	params[VS_LOWER] = lower_bound;
	params[VS_BASE] = base;
	params[VS_CURRENT] = base;
	params[VS_UPPER] = upper_bound;
	fluctuation_coefficient = randomFloat(.02, .05, 4);
	fluctuation_sensitivity = randomFloat(.02, .2, 4);
	update();
}

value_state::value_state(float lower_min, float upper_max)
{
	setBounds(lower_min, upper_max);
	setBase();
	params[VS_CURRENT] = params[VS_BASE];
	fluctuation_coefficient = randomFloat(.02, .05, 4);
	fluctuation_sensitivity = randomFloat(.02, .2, 4);
	update();
}

const bool value_state::proc() const
{
	float random_float = randomFloat(0.0f, 100.0f, 2);
	if (random_float < params.at(VS_CURRENT))
		return true;

	else return false;
}

void value_state::setBounds(float lower_min, float upper_max)
{
	float span = upper_max - lower_min;
	signed short probability_array[] = { 18, 20, 24, 20, 18 };

	map< floatpair, signed short> lower_quadrants;
	for (int i = 0; i < 5; i++)
	{
		float quadrant_range_lower = lower_min + ((.1 * i) * span);
		float quadrant_range_upper = lower_min + ((.1 * (i + 1)) * span);
		lower_quadrants[floatpair(quadrant_range_lower, quadrant_range_upper)] = probability_array[i];
	}
	floatpair selected_lower_quadrant = jep::catRoll<floatpair>(lower_quadrants);
	params[VS_LOWER] = randomFloat(selected_lower_quadrant.first, selected_lower_quadrant.second, 2);

	map< floatpair, signed short> upper_quadrants;
	for (int i = 0; i < 5; i++)
	{
		float quadrant_range_lower = lower_min + ((.1 * (i + 5)) * span);
		float quadrant_range_upper = lower_min + ((.1 * (i + 6)) * span);
		upper_quadrants[floatpair(quadrant_range_lower, quadrant_range_upper)] = probability_array[i];
	}
	floatpair selected_upper_quadrant = jep::catRoll<floatpair>(upper_quadrants);
	params[VS_UPPER] = randomFloat(selected_upper_quadrant.first, selected_upper_quadrant.second, 2);
}

void value_state::setBase()
{
	float lowest = params.at(VS_LOWER);
	float span = params.at(VS_UPPER) - params.at(VS_LOWER);
	signed short probability_array[] = { 18, 20, 24, 20, 18 };

	map< floatpair, signed short> base_quadrants;
	for (int i = 0; i < 5; i++)
	{
		float quadrant_range_lower = lowest + ((.1 * i) * span);
		float quadrant_range_upper = lowest + ((.1 * (i + 1)) * span);
		base_quadrants[floatpair(quadrant_range_lower, quadrant_range_upper)] = probability_array[i];
	}
	floatpair selected_base_quadrant = jep::catRoll<floatpair>(base_quadrants);
	params[VS_BASE] = randomFloat(selected_base_quadrant.first, selected_base_quadrant.second, 2);
}

void value_state::fluctuate()
{
	float positive_chance;

	//When current level is the base level, there's a 50/50 chance for the trait to fluctuate positively.
	//The closer the current level is to upper bound, the less likely it is to change in the positive. Same
	//mechanic when current is close to lower bound.

	if (params.at(VS_CURRENT) >= params.at(VS_BASE))
	{
		float distance_from_upper = params.at(VS_UPPER) - params.at(VS_CURRENT);
		float upper_range = params.at(VS_UPPER) - params.at(VS_BASE);
		positive_chance = (distance_from_upper / upper_range) * .5f;
	}

	else
	{
		float distance_from_lower = params.at(VS_CURRENT) - params.at(VS_LOWER);
		float lower_range = params.at(VS_BASE) - params.at(VS_LOWER);
		positive_chance = 1 - ((distance_from_lower / lower_range) * .5f);
	}

	float value_change = randomFloat(0.0f, fluctuation_coefficient, 3) * (params.at(VS_UPPER) - params.at(VS_LOWER));

	if (!booRoll(positive_chance))
		value_change *= -1.0f;

	params[VS_CURRENT] = params[VS_CURRENT] += value_change;

	update();
}

void value_state::update()
{
	VSBoundsCheck();
	float distance_from_lower = params.at(VS_CURRENT) - params.at(VS_LOWER);
	float range = params.at(VS_UPPER) - params.at(VS_LOWER);
	params[VS_RELATIVE] = distance_from_lower / range;
	params[VS_COEF] = params[VS_CURRENT] / 100.0f;
}

void value_state::influence(float value, float coefficient = -1.0f)
{
	if (coefficient < 0)
		coefficient = fluctuation_sensitivity;

	float distance_from_current = params.at(VS_CURRENT) - value;
	float value_change = distance_from_current * coefficient;
	params[VS_CURRENT] += value_change;
	VSBoundsCheck();
}

void value_state::VSBoundsCheck()
{
	if (params.at(VS_CURRENT) > params.at(VS_UPPER))
		params[VS_CURRENT] = params[VS_UPPER];

	else if (params.at(VS_CURRENT) < params.at(VS_LOWER))
		params[VS_CURRENT] = params[VS_LOWER];
}

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

float boundsCheck(float f)
{
	if (f > 100)
		return 100.0;

	else if (f < 0)
		return 0.0;

	else return f;
}

const string generateID(string name)
{
	string ID = name;

	for (int i = 0; i < 12; i++)
	{
		char c = '0';
		c += rand() % 10;
		ID += c;
	}

	return ID;
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