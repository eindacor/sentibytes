#ifndef SB_GRAPHICS_H
#define SB_GRAPHICS_H

#include "sb_header.h"
#include "sb_sentibyte.h"

class sentibyte_geometry
{
public:
	sentibyte_geometry(sb_ptr &sb, vec4 b);
	~sentibyte_geometry(){};

	const bool operator == (const string &s) const { return getID() == s; }
	const bool operator == (const sentibyte_geometry &other) const { return getID() == other.getID(); }

	void updateGeometry();
	void draw(GLuint VBO, GLint sb_color_ID);
	const string getID() const { return host->getID(); }
	void moveBasePoint(mat4 tm) { base_point = tm * base_point; }
	const vec4 getColor() const { return sb_color; };

private:
	map<string, glm::vec4> vertices;
	glm::vec4 base_point;
	sb_ptr host;
	vec4 sb_color;

};

class sb_group
{
public:
	sb_group(): cursor(0.0f, 0.0f, 0.0f, 1.0f) {};
	~sb_group(){};

	void draw(GLuint VBO, GLint sb_color_ID);
	void addSBGeometry(sb_ptr &added_sb);
	void removeSBGeometry(sb_ptr &to_remove);
	const signed short getSBCount() const { return sb_vector.size(); }
	const vec4 getCursor() const { return cursor; }
	const signed short getCount() const { return sb_vector.size(); }
	void clear() { sb_vector.clear(); }

	string convertCurrentLine();

private:
	vec4 cursor;
	vector<sentibyte_geometry> sb_vector;
	int current_range;
};

#endif