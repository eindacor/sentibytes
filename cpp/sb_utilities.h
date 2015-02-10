#ifndef SB_UTILITIES_H
#define SB_UTILITIES_H

#include "sb_header.h"

float boundsCheck(float f);
float calcAccuracy(float target_value, float range_coefficient, float max_offset = 10.0);
const bool stringInVector(string s, const vec_str &vec);

template <typename t>
const vector<t>::const_iterator randomVectorIterator(const vector<t> &vec);

template <typename t1, typename t2>
const map<t1, t2>::const_iterator randomMapIterator(const map<t1, t2> &m);

template <typename t>
void removeFromVector(vector<t> &vec, t target);

template <typename t1, typename t2>
void removeFromMap(map<t1, t2> &m, t1 target);

class value_state
{
public:
	value_state(float lower_min, float upper_max);
	~value_state(){};

	const bool proc() const;
	const float operator [] (string trait) const { return params.at(trait); }
	void fluctuate();

private:
	map<string, float> params;

};

class avg_container
{
public:
	avg_container() : average(0.0), count(0) {};
	avg_container(float avg, int c) : average(avg), count(c) {};
	~avg_container(){};

	const float combineAverages(float previous_avg, int previous_count, float new_avg, int new_count) const;
	void addValue(float value) { average = combineAverages(average, count, value, 1); count++; }
	void addAverage(float added_avg, int added_count) { 
		average = combineAverages(average, count, added_avg, added_count); count += added_count; }
	void operator = (const avg_container &other) {
		average = other.getAverage(); count = other.getCount();}

	const float getAverage() const { return average; }
	const signed long getCount() const { return count; }

private:
	float average;
	signed long count;
};

template <typename T>
class list_manager
{
public:
	list
private:

};

#endif