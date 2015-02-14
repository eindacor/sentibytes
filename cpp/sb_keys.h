#ifndef SB_KEYS_H
#define SB_KEYS_H

#include "sb_header.h"

class key_handler
{
public:
	key_handler(){};
	~key_handler(){};

	bool checkPress(int key, GLFWwindow* window);
	KEYRETURN key_handler::checkKeys(display_handler &display_context);

private:
	list<int> keysPressed;

};

#endif