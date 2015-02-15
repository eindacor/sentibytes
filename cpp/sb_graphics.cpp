#include "sb_graphics.h"


sentibyte_geometry::sentibyte_geometry(sb_ptr &sb, vec4 b)
{
	base_point = b;
	host = sb;

	sb_color[0] = randomFloat(0.0f, 1.0f, 2);
	sb_color[1] = randomFloat(0.0f, 1.0f, 2);
	sb_color[2] = randomFloat(0.0f, 1.0f, 2);

	signed short radial_divisions = host->getTraitCount();
	mat4 rotation_matrix = glm::rotate(mat4(1.0f), 360.0f / float(radial_divisions), vec3(0.0f, 0.0f, 1.0f));

	for (int i = 0; i < host->getTraitCount(); i++)
	{
		float outline_thickness = .02f;
		vec4 max_point(0.0f, 1.0, 0.0f, 1.0f);
		vec4 outline_point(0.0f, 1.0 + outline_thickness, 0.0f, 1.0f);

		// rotate point around the center axis
		for (int n = 0; n < i; n++)
		{
			max_point = rotation_matrix * max_point;
			outline_point = rotation_matrix * outline_point;
		}

		mat4 base_translation = glm::translate(
			glm::mat4(1.0f), vec3(base_point.x, base_point.y, base_point.z));

		max_point = base_translation * max_point;
		outline_point = base_translation * outline_point;

		max_levels.push_back(max_point);
		outline.push_back(outline_point);
	}

	map<string, value_state> trait_map = host->getTraits();
	signed short trait_number = 0;
	for (map<string, value_state>::const_iterator it = trait_map.begin();
		it != trait_map.end(); it++)
	{
		string trait_name = it->first;

		float base_coefficient = it->second[VS_BASE] / 100.0f;
		float upper_coefficient = it->second[VS_UPPER] / 100.0f;
		float lower_coefficient = it->second[VS_LOWER] / 100.0f;

		vec4 base_level_point(0.0f, base_coefficient, 0.0f, 1.0f);
		vec4 lower_point(0.0f, lower_coefficient, 0.0f, 1.0f);
		vec4 upper_point(0.0f, upper_coefficient, 0.0f, 1.0f);

		// rotate point around the center axis
		for (int i = 0; i < trait_number; i++)
		{
			base_level_point = rotation_matrix * base_level_point;
			lower_point = rotation_matrix * lower_point;
			upper_point = rotation_matrix * upper_point;
		}

		mat4 base_translation = glm::translate(
			glm::mat4(1.0f), vec3(base_point.x, base_point.y, base_point.z));

		base_level_point = base_translation * base_level_point;
		lower_point = base_translation * lower_point;
		upper_point = base_translation * upper_point;

		base_levels[trait_name] = base_level_point;
		upper_bounds[trait_name] = upper_point;
		lower_bounds[trait_name] = lower_point;

		trait_number++;
	}
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

		float coefficient = it->second[VS_COEF];

		vec4 trait_point(0.0f, coefficient, 0.0f, 1.0f);

		// rotate point around the center axis
		for (int i = 0; i < trait_number; i++)
			trait_point = rotation_matrix * trait_point;

		mat4 base_translation = glm::translate(
			glm::mat4(1.0f), vec3(base_point.x, base_point.y, base_point.z));

		trait_point = base_translation * trait_point;

		vertices[trait_name] = trait_point;

		trait_number++;
	}
}

void sentibyte_geometry::draw(GLuint VBO, GLint sb_color_ID, vec4 background_color)
{
	updateGeometry();
	vec4 default_outline_color;
	if (background_color.x + background_color.y + background_color.z < 1.5f)
		default_outline_color = vec4(1.0f, 1.0f, 1.0f, 1.0f);

	else default_outline_color = vec4(0.0f, 0.0f, 0.0f, 0.0f);

	vec4 outline_color = combineColors(default_outline_color, background_color, .5f);
	glUniform4f(sb_color_ID, outline_color[0], outline_color[1], outline_color[2], outline_color[3]);
	for (vector<vec4>::const_iterator it = outline.begin(); it != outline.end(); it++)
	{
		vector<vec4>::const_iterator next = it;
		next++;
		vec4 point_one = base_point;
		if (next == outline.end())
			next = outline.begin();
		vec4 point_two = *next;
		vec4 point_three = *it;

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

	//create color that is a combination of the background and text colors, and modify the uniform for the faded version
	vec4 max_levels_color;
	if (host->proc("positivity") && host->proc("positivity") && host->proc("positivity"))
		max_levels_color = combineColors(sb_color, background_color, .3f);
	else max_levels_color = combineColors(sb_color, background_color, .2f);
	glUniform4f(sb_color_ID, max_levels_color[0], max_levels_color[1], max_levels_color[2], max_levels_color[3]);
	for (vector<vec4>::const_iterator it = max_levels.begin(); it != max_levels.end(); it++)
	{	
		vector<vec4>::const_iterator next = it;
		next++;
		vec4 point_one = base_point;
		if (next == max_levels.end())
			next = max_levels.begin();
		vec4 point_two = *next;
		vec4 point_three = *it;
		
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

	//set sb color
	vec4 upper_bounds_color = combineColors(sb_color, background_color, .4f);
	glUniform4f(sb_color_ID, upper_bounds_color[0], upper_bounds_color[1], upper_bounds_color[2], 1.0f);
	for (map<string, glm::vec4>::const_iterator it = upper_bounds.begin(); it != upper_bounds.end(); it++)
	{
		map<string, glm::vec4>::const_iterator next = it;
		next++;
		vec4 point_one = base_point;
		if (next == upper_bounds.end())
			next = upper_bounds.begin();
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

	vec4 base_level_color = max_levels_color;
	glUniform4f(sb_color_ID, base_level_color[0], base_level_color[1], base_level_color[2], 1.0f);
	for (map<string, glm::vec4>::const_iterator it = base_levels.begin(); it != base_levels.end(); it++)
	{
		map<string, glm::vec4>::const_iterator next = it;
		next++;
		vec4 point_one = base_point;
		if (next == base_levels.end())
			next = base_levels.begin();
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

	//set sb color
	glUniform4f(sb_color_ID, sb_color[0], sb_color[1], sb_color[2], 1.0f);
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

void sentibyte_geometry::moveBasePoint(mat4 tm) 
{ 
	base_point = tm * base_point; 
	for (vector<vec4>::iterator it = max_levels.begin(); it != max_levels.end(); it++)
		*it = tm * (*it);
}

void sb_group::draw(GLuint VBO, GLint sb_color_ID, vec4 background_color)
{
	for (vector<sentibyte_geometry>::iterator it = sb_vector.begin(); it != sb_vector.end(); it++)
		it->draw(VBO, sb_color_ID, background_color);
}

void sb_group::addSBGeometry(sb_ptr &to_add)
{
	sb_vector.push_back(sentibyte_geometry(to_add, cursor));

	//2.0 is the default width of a sentibyte_geometry
	float x_offset = 2.0f;
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