#ifndef SB_UTILITIES_H
#define SB_UTILITIES_H

#include "sb_header.h"

float boundsCheck(float f);
float calcAccuracy(float target_value, float range_coefficient, float max_offset);
const bool stringInVector(string s, const vec_str &vec);
const float getCoefficient(float min, float max);

typedef pair<float, float> floatpair;

class value_state
{
public:
	value_state();
	value_state(float lower_bound, float base, float upper_bound);
	value_state(float lower_min, float upper_max);
	~value_state(){};

	const bool proc() const;
	const float operator [] (value_state_data_type type) const { return params.at(type); }
	void fluctuate();
	void update();
	void influence(float value, float coefficient);
	void setFlucCoefficient(float f) { fluctuation_coefficient = f; }
	void setFlucSensitivity(float f) { fluctuation_sensitivity = f; }

private:
	void setBounds(float lower_min, float upper_max);
	void setBase();
	void VSBoundsCheck();
	map<value_state_data_type, float> params;
	float fluctuation_coefficient;
	float fluctuation_sensitivity;
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

template<typename T>
class list_manager
{
public:
	list_manager(){};
	~list_manager(){};

	void addList(string list_name);
	void removeList(string list_name);
	void addToList(T to_add, string list_name) { lists.at(list_name).push_back(to_add); }
	void removeFromList(T to_add, string list_name) { lists.at(list_name).remove(to_add); }
	const bool isInList(T to_add, string list_name) const;
	const list<string> getList(string list_name) const { return lists.at(list_name); }
	const signed int getListSize(string list_name) const { return lists.at(list_name).size(); }

private:
	map<string, list<T> > lists;
};

#endif