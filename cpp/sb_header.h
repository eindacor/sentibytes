#ifndef SB_HEADER_H
#define SB_HEADER_H

#include <iostream>
#include <string>
#include <vector>
#include <stdlib.h>
#include <time.h>
#include <map>
#include <algorithm>
#include <boost/smart_ptr/shared_ptr.hpp>
#include "jeploot.h"

class perception;
class interaction;
class sentibyte;
class population;
class session;

#include "sb_utilities.h"

using std::string;
using std::vector;
using std::map;
using std::endl;
using std::cout;
using std::cin;
using std::pair;
using std::sort;

enum transmission_type { STATEMENT, SIGNAL, NO_T_TYPE };
enum definition {COMMUNICATIONS_PER_CYCLE=20, MAX_FRIENDS=12, CHILD_AGE=40, MAX_MEMORIES=8,
					BOND_POINT=50, MAX_CHILDREN=3};

typedef map<string, perception> perception_map;
typedef perception_map::const_iterator perception_iterator;
typedef map<string, vector<interaction>> memory_map;
typedef memory_map::const_iterator memory_iterator;
typedef vector<string> vec_str;
typedef vector<string>::const_iterator vec_str_it;
typedef boost::shared_ptr<session> session_ptr;
typedef boost::shared_ptr<population> population_ptr;
typedef boost::shared_ptr<contactManager> contacts_ptr;
typedef boost::shared_ptr<sentibyte> sb_ptr;

#endif