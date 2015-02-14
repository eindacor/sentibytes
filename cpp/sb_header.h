#ifndef SB_HEADER_H
#define SB_HEADER_H

//headers required for opengl
#include <glew.h>
#include <glfw3.h>
#include <glm.hpp>
#include <gtc/matrix_transform.hpp>
#include <fstream>

#include <iostream>
#include <string>
#include <vector>
#include <list>
#include <stdlib.h>
#include <stdarg.h>
#include <random>
#include <time.h>
#include <map>
#include <math.h>
#include <algorithm>
#include <boost/smart_ptr/shared_ptr.hpp>
#include "jeploot.h"

class perception;
class interaction;
class sentibyte;
class population;
class session;
class contact_manager;
class value_state;
class display_handler;
class key_handler;
template <typename T> class list_manager;

using std::string;
using std::vector;
using std::map;
using std::endl;
using std::cout;
using std::cin;
using std::pair;
using std::sort;
using std::list;
using jep::booRoll;
using jep::catRoll;

//opengl
using glm::mat4;
using glm::vec4;
using glm::vec3;
enum opengl_defs { MARGAINS = 1, DEFAULT_SB_WIDTH = 2, VERTICAL_PADDING = 2};
enum KEYRETURN { NULL_RETURN, ENTER, BASE, OPTIONS };

typedef boost::shared_ptr<population> population_ptr;
typedef boost::shared_ptr<contact_manager> contacts_ptr;
typedef boost::shared_ptr<sentibyte> sb_ptr;
typedef boost::shared_ptr<perception> perception_ptr;
typedef list_manager<string> string_list_manager;
typedef boost::shared_ptr<string_list_manager> string_listman_ptr;

typedef map<std::string, perception_ptr> perception_map;
typedef perception_map::const_iterator perception_iterator;
typedef vector<float> vec_float;
typedef map<string, vec_float> memory_map;
typedef memory_map::const_iterator memory_iterator;
typedef vector<string> vec_str;
typedef vector<string>::const_iterator vec_str_iterator;

enum transmission_type { STATEMENT, SIGNAL, NO_T_TYPE };
enum definition {COMMUNICATIONS_PER_CYCLE=20, MAX_FRIENDS=12, CHILD_AGE=40, MAX_MEMORIES=8,
					BOND_POINT=50, MAX_CHILDREN=3};
enum sb_status {ALONE, IN_OPEN_SESSION, IN_FULL_SESSION};
enum invitation_type {STRANGERS, FRIENDS, CONTACTS, FAMILY};
enum value_state_data_type { VS_LOWER, VS_BASE, VS_UPPER, VS_CURRENT, VS_COEF, VS_RELATIVE };

#include "sb_utilities.h"

#endif