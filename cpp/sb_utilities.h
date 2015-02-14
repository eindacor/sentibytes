#ifndef SB_UTILITIES_H
#define SB_UTILITIES_H

#include "sb_header.h"

float boundsCheck(float f);
float calcAccuracy(float target_value, float range_coefficient, float max_offset);
const bool stringInVector(string s, const vec_str &vec);
const bool stringInList(string s, const list<string> &str);
const float getCoefficient(float min, float max);
const string generateID(string name);
const float randomFloat(float min, float max, int precision);
const vec4 combineColors(vec4 primary, vec4 secondary, float blend);

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
	const float fluctuate();
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

	inline void addList(string list_name);
	inline void removeList(string list_name);
	void addToList(T to_add, string list_name) { lists.at(list_name).push_back(to_add); }
	void removeFromList(T to_add, string list_name) { lists.at(list_name).remove(to_add); }
	inline const bool isInList(T to_find, string list_name) const;
	const list<T> getList(string list_name) const { return lists.at(list_name); }
	const signed int getListSize(string list_name) const { return lists.at(list_name).size(); }
	void removeFromAllLists(T to_remove);
	const vector<string> getListNames() const;

private:
	map<string, list<T> > lists;
};

template <typename T>
void list_manager<T>::addList(string list_name)
{
	if (lists.find(list_name) == lists.end())
		lists[list_name] = list<string>();
}

template <typename T>
void list_manager<T>::removeList(string list_name)
{
	lists.at(list_name);
	lists.erase(list_name);
}

template <typename T>
const bool list_manager<T>::isInList(T to_find, string list_name) const
{
	list<T>::const_iterator it =
		std::find(lists.at(list_name).begin(), lists.at(list_name).end(), to_find);

	return it != lists.at(list_name).end();
}

template <typename T>
void list_manager<T>::removeFromAllLists(T to_remove)
{
	for (map<string, list<T> >::iterator it = lists.begin(); it != lists.end(); it++)
		it->second.remove(to_remove);
}

template <typename T>
const vector<string> list_manager<T>::getListNames() const
{
	vector<string> list_names;
	for (map < string, list<T> >::const_iterator it = lists.begin(); it != lists.end(); it++)
		list_names.push_back(it->first);

	return list_names;
}

template <typename T>
const T randomVectorElement(const vector<T> &vec)
{
	if (vec.size() == 0)
		throw;

	int random_index = rand() % vec.size();
	vector<T>::const_iterator it = vec.begin() + random_index;
	return T(*it);
}

template <typename T1, typename T2>
const pair<T1, T2> randomMapElement(const map<T1, T2> &m)
{
	if (m.size() == 0)
		throw;

	int random_index = rand() % m.size();
	map<T1, T2>::const_iterator it = m.cbegin();
	for (int i = 0; i < random_index; i++)
		it++;

	return pair<T1, T2>(it->first, it->second);
}

#endif