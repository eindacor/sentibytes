#version 330

layout (location = 0) in vec4 position;

uniform mat4 translation_matrix;
uniform mat4 scaling_matrix;
uniform vec4 text_color;

smooth out vec4 fragment_color;

void main()
{
	gl_Position = scaling_matrix * translation_matrix * position;
	fragment_color = text_color;
}