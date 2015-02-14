#include "sb_keys.h"
#include "sb_display.h"

bool key_handler::checkPress(int key, GLFWwindow* window)
{
	int state = glfwGetKey(window, key);

	//check list of keys pressed for a match, acts according to the press state
	for (list<int>::iterator i = keysPressed.begin(); i != keysPressed.end(); ++i)
	{
		if (*i == key)
		{
			if (state == GLFW_RELEASE)
				keysPressed.erase(i);
			return false;
		}
	}

	switch (state)
	{
	case GLFW_PRESS: keysPressed.push_back(key); return true;
	case GLFW_RELEASE: return false;
	default: return false;
	}
}

KEYRETURN key_handler::checkKeys(display_handler &display_context)
{
	GLFWwindow* window = display_context.getWindow();

	if (checkPress(GLFW_KEY_ENTER, window))
	{
		return ENTER;
		//lines.addLine(line(origin));
		//entered = lines.convertCurrentLine();
		//solution answer = solve(entered, previous, user_settings);
	}

	if (checkPress(GLFW_KEY_UP, window))
	{
		display_context.scrollSentibyteColor(1);
	}

	if (checkPress(GLFW_KEY_DOWN, window))
	{
		display_context.scrollSentibyteColor(-1);
	}

	if (checkPress(GLFW_KEY_LEFT, window))
	{
		display_context.scrollBackgroundColor(1);
	}

	if (checkPress(GLFW_KEY_RIGHT, window))
	{
		display_context.scrollBackgroundColor(-1);
	}

	return NULL_RETURN;
}