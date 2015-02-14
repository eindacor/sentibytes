#ifndef SB_DISPLAY_H
#define SB_DISPLAY_H

#include "sb_header.h"
#include "sb_graphics.h"

class display_handler
{
public:
	display_handler(string title, string vert_file, string frag_file);
	~display_handler();

	void printErrors();

	GLFWwindow* getWindow() { return window; }

	bool getErrors() { return errors; }

	void render(sb_group &sbg);
	void scrollSentibyteColor(int i);
	void scrollBackgroundColor(int i);
	int createProgram(string vert_file, string frag_file);
	int createShader(GLenum type, string file);

private:
	GLuint program_ID;
	GLuint fragment_shader_ID;
	GLuint vertex_shader_ID;
	GLint translation_matrix_ID;
	GLint scaling_matrix_ID;
	GLint sb_color_ID;
	vec4 text_color;
	vec4 background_color;
	GLFWwindow* window;
	vector<string> display_errors;
	bool errors = true;
	string window_title;
	int sentibyte_color_index;
	int background_color_index;

	GLuint vertex_buffer_object;
	GLuint vertex_array_object;
};

#endif