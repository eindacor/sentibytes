#include "sb_utilities.h"

const float avgContainer::combineAverages
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

float calcAccuracy(float target_value, float range_coefficient, float max_offset=10.0)
{
	float random_float = float(rand() % 101) / 100.0f;
	float margain = max_offset * range_coefficient * random_float;
	if (rand() % 2 == 0)
		margain *= -1;
	float new_value = boundsCheck(target_value + margain);
	return new_value;
}