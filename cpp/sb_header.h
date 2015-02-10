#ifndef SB_HEADER_H
#define SB_HEADER_H

#include <iostream>
#include <string>
#include <vector>
#include <list>
#include <stdlib.h>
#include <stdarg.h>
#include <random>
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
class contactManager;

#include "sb_utilities.h"

using std::string;
using std::vector;
using std::map;
using std::endl;
using std::cout;
using std::cin;
using std::pair;
using std::sort;
using std::shuffle;
using std::begin;
using std::end;
using std::list;

enum transmission_type { STATEMENT, SIGNAL, NO_T_TYPE };
enum definition {COMMUNICATIONS_PER_CYCLE=20, MAX_FRIENDS=12, CHILD_AGE=40, MAX_MEMORIES=8,
					BOND_POINT=50, MAX_CHILDREN=3};
enum sb_status {ALONE, IN_OPEN_SESSION, IN_FULL_SESSION};
enum invitation_type {STRANGERS, FRIENDS, CONTACTS, FAMILY};

typedef boost::shared_ptr<session> session_ptr;
typedef boost::shared_ptr<population> population_ptr;
typedef boost::shared_ptr<contactManager> contacts_ptr;
typedef boost::shared_ptr<sentibyte> sb_ptr;
typedef boost::shared_ptr<perception> perception_ptr;
typedef boost::shared_ptr<interaction> interaction_ptr;
typedef boost::shared_ptr< list_manager<string> > string_listman_ptr;

typedef map<string, perception_ptr> perception_map;
typedef perception_map::const_iterator perception_iterator;
typedef map<string, vector<interaction_ptr>> memory_map;
typedef memory_map::const_iterator memory_iterator;
typedef vector<string> vec_str;
typedef vector<string>::const_iterator vec_str_it;

#endif