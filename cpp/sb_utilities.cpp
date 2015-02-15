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

const bool stringInList(string s, const list<string> &str)
{
	return std::find(str.begin(), str.end(), s) != str.end();
}

value_state::value_state()
{
	setBounds(0.0f, 100.0f);
	setBase();
	params[VS_CURRENT] = params[VS_BASE];
	setFluctuationValues();
	update();
}

value_state::value_state(float lower_bound, float base, float upper_bound)
{
	params[VS_LOWER] = lower_bound;
	params[VS_BASE] = base;
	params[VS_CURRENT] = base;
	params[VS_UPPER] = upper_bound;
	setFluctuationValues();
	update();
}

value_state::value_state(float lower_min, float upper_max)
{
	setBounds(lower_min, upper_max);
	setBase();
	params[VS_CURRENT] = params[VS_BASE];
	setFluctuationValues();
	update();
}

void value_state::setFluctuationValues()
{
	fluctuation_coefficient = randomFloat(.08, .15, 2);
	fluctuation_sensitivity = randomFloat(.2, .3, 2);
	fluctuation_cooldown = 0;
	fluctuation_increment = 0.0f;
	default_fluctuation_duration = 64;
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
	params[VS_LOWER] = randomFloat(selected_lower_quadrant.first, selected_lower_quadrant.second, 2) * 100.0f;

	map< floatpair, signed short> upper_quadrants;
	for (int i = 0; i < 5; i++)
	{
		float quadrant_range_lower = lower_min + ((.1 * (i + 5)) * span);
		float quadrant_range_upper = lower_min + ((.1 * (i + 6)) * span);
		upper_quadrants[floatpair(quadrant_range_lower, quadrant_range_upper)] = probability_array[i];
	}
	floatpair selected_upper_quadrant = jep::catRoll<floatpair>(upper_quadrants);
	params[VS_UPPER] = randomFloat(selected_upper_quadrant.first, selected_upper_quadrant.second, 2) * 100.0f;
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

const float value_state::fluctuate()
{
	if (fluctuation_cooldown == 0)
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

		float total_range = params.at(VS_UPPER) - params.at(VS_LOWER);
		float value_change = randomFloat(0.0f * fluctuation_coefficient, fluctuation_coefficient, 3) * total_range;

		if (!booRoll(positive_chance))
			value_change *= -1.0f;

		// instead of changing value immediately, set the increment and change over time
		fluctuation_increment = value_change / float(default_fluctuation_duration);
		fluctuation_cooldown = default_fluctuation_duration;
		params[VS_CURRENT] += fluctuation_increment;

		update();
		return fluctuation_increment;
	}

	else
	{
		fluctuation_cooldown--;
		params[VS_CURRENT] += fluctuation_increment;

		update();
		return fluctuation_increment;
	}
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
	string ID = name + '_';

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

const vec4 combineColors(vec4 primary, vec4 secondary, float blend)
{
	float primary_ratio = blend;
	float secondary_ratio = 1.0f - blend;
	float combined_red = (primary[0] * primary_ratio) + (secondary[0] * secondary_ratio);
	float combined_green = (primary[1] * primary_ratio) + (secondary[1] * secondary_ratio);
	float combined_blue = (primary[2] * primary_ratio) + (secondary[2] * secondary_ratio);
	float combined_alpha = (primary[3] * primary_ratio) + (secondary[3] * secondary_ratio);

	return vec4(combined_red, combined_green, combined_blue, combined_alpha);
}

const pair<float, float> calculateLineFormula(vec2 first, vec2 second)
{
	if (abs(first.y - second.y) < .00000001f)
		return pair<float, float>(0.0f, second.y);

	float multiplier = (second.y - first.y) / (second.x - first.x);
	float y_offset = first.y - (first.x * multiplier);
	return pair<float, float>(multiplier, y_offset);
}

const float getLineAngle(vec2 first, vec2 second)
{
	if (abs(first.x - second.x) < .00000001f)
		return 90.0f;
	vec2 left_most = (first.x < second.x ? first : second);
	vec2 right_most = (first.x > second.x ? first : second);
	float pi = 3.14159265;
	float angle = atan(abs(right_most.y - left_most.y) / abs(right_most.x - left_most.x)) * (180 / pi);
	if (left_most.y > right_most.y)
		return 180.0f - angle;
	else return angle;
}

const pair<vec2, vec2> getOffsetPoints(vec2 first, vec2 second, float distance, bool below)
{
	vec2 left_most = (first.x < second.x ? first : second);
	vec2 right_most = (first.x > second.x ? first : second);
	float line_angle = getLineAngle(first, second);
	vec4 first_point(0.0f, 0.0f, 0.0f, 1.0f);

	glm::mat4 distance_offset = glm::translate(mat4(1.0f), vec3(0.0f + distance, 0.0f, 0.0f));

	float rotation_angle;
	//rotation angles assume clockwise
	if (below)
		rotation_angle = (line_angle < 90.0f ? (90.0f - line_angle) : (270.0f - line_angle));

	else rotation_angle = -1.0f * (line_angle + 90.0f);

	mat4 rotation_matrix = glm::rotate(mat4(1.0f), rotation_angle, vec3(0.0f, 0.0f, 1.0f));
}