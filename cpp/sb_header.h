#ifndef SB_HEADER_H
#define SB_HEADER_H

#include <iostream>
#include <string>
#include <vector>
#include <stdlib.h>
#include <time.h>
#include <map>
#include <algorithm>

class perception;
class interaction;
class sentibyte;
class community;
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
enum definition {COMMUNICATIONS_PER_CYCLE=20, MAX_FRIENDS=12, CHILD_AGE=40};

typedef map<string, perception> perception_map;
typedef perception_map::const_iterator perception_iterator;
typedef map<string, vector<interaction>> memory_map;
typedef memory_map::const_iterator memory_iterator;

#endif