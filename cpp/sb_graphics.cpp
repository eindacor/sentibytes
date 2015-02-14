#include "sb_graphics.h"


sentibyte_geometry::sentibyte_geometry(sb_ptr &sb, vec4 b)
{
	base_point = b;
	host = sb;

	sb_color[0] = randomFloat(0.0f, 1.0f, 2);
	sb_color[1] = randomFloat(0.0f, 1.0f, 2);
	sb_color[2] = randomFloat(0.0f, 1.0f, 2);
}

void sentibyte_geometry::updateGeometry()
{
	signed short radial_divisions = host->getTraitCount();

	mat4 rotation_matrix = glm::rotate(mat4(1.0f), 360.0f / float(radial_divisions), vec3(0.0f, 0.0f, 1.0f));

	signed short trait_number = 0;

	map<string, value_state> trait_map = host->getTraits();
	for (map<string, value_state>::const_iterator it = trait_map.begin();
		it != trait_map.end(); it++)
	{
		string trait_name = it->first;
		//cout << "trait: " << trait_name << endl;
		float coefficient = it->second[VS_COEF];
		//cout << "coeff: " << coefficient << endl;

		vec4 trait_point(0.0f, coefficient, 0.0f, 1.0f);
		//cout << "x: " << trait_point.x << endl;
		//cout << "y: " << trait_point.y << endl;
		//cout << "z: " << trait_point.z << endl;

		// rotate point around the center axis
		for (int i = 0; i < trait_number; i++)
			trait_point = rotation_matrix * trait_point;

		//cout << "after rotation:" << endl;
		//cout << "x: " << trait_point.x << endl;
		//cout << "y: " << trait_point.y << endl;
		//cout << "z: " << trait_point.z << endl;

		mat4 base_translation = glm::translate(
			glm::mat4(1.0f), vec3(base_point.x, base_point.y, base_point.z));

		trait_point = base_translation * trait_point;

		//cout << "after translation:" << endl;
		//cout << "x: " << trait_point.x << endl;
		//cout << "y: " << trait_point.y << endl;
		//cout << "z: " << trait_point.z << endl;
		//cout << "--------" << endl;

		vertices[trait_name] = trait_point;

		trait_number++;
	}
}

void sentibyte_geometry::draw(GLuint VBO, GLint sb_color_ID)
{
	//set sb color
	glUniform4f(sb_color_ID, sb_color[0], sb_color[1], sb_color[2], 1.0f);

	updateGeometry();
	for (map<string, glm::vec4>::const_iterator it = vertices.begin(); it != vertices.end(); it++)
	{	
		map<string, glm::vec4>::const_iterator next = it;
		next++;
		vec4 point_one = base_point;
		if (next == vertices.end())
			next = vertices.begin();
		vec4 point_two = next->second;
		vec4 point_three = it->second;
		//*/
		
		vec4 indices[3] = { point_one, point_two, point_three };
		//bind vbo
		glBindBuffer(GL_ARRAY_BUFFER, VBO);
		//pass data to GPU
		glBufferData(GL_ARRAY_BUFFER, sizeof(indices), indices, GL_STATIC_DRAW);
		//use vertex attrib pointer to instruct OpenGLU how to interpret the data on the buffer
		glEnableVertexAttribArray(0);
		glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 0, (void*)0);
		//draws vertices (2 triangles per "pixel")
		glDrawArrays(GL_TRIANGLES, 0, 3);

		//disable array/unbind vbo
		glDisableVertexAttribArray(0);
		glBindBuffer(GL_ARRAY_BUFFER, 0);
	}	
}

void sb_group::draw(GLuint VBO, GLint sb_color_ID)
{
	for (vector<sentibyte_geometry>::iterator it = sb_vector.begin(); it != sb_vector.end(); it++)
		it->draw(VBO, sb_color_ID);
}

void sb_group::addSBGeometry(sb_ptr &to_add)
{
	sb_vector.push_back(sentibyte_geometry(to_add, cursor));

	float x_offset = DEFAULT_SB_WIDTH + .5f;
	mat4 cursor_translate = glm::translate(mat4(1.0f), vec3(x_offset, 0.0f, 0.0f));
	cursor = cursor_translate * cursor;
}

void sb_group::removeSBGeometry(sb_ptr &to_remove)
{
	vector<sentibyte_geometry>::iterator it_found = std::find(sb_vector.begin(), sb_vector.end(), to_remove->getID());
	if (it_found != sb_vector.end())
	{
		bool item_found = false;

		float x_offset = DEFAULT_SB_WIDTH + .5f;
		x_offset *= -1.0f;
		mat4 x_translate = glm::translate(mat4(1.0f), vec3(x_offset, 0.0f, 0.0f));
		cursor = x_translate * cursor;

		// shift all other sb's to the left
		for (vector<sentibyte_geometry>::iterator it = sb_vector.begin(); it != sb_vector.end(); it++)
		{
			if (item_found)
				it->moveBasePoint(x_translate);

			if (it == it_found)
				item_found = true;
		}
	
		sb_vector.erase(it_found);
	}

	//possibly throw an exception to make sure code is efficient, not trying to remove sb's that aren't there
}