#include <iostream>
#include "sb_sentibyte.h"
#include "sb_display.h"
#include "sb_keys.h"

void printList(const sentibyte &sb, string list_name)
{
	cout << sb.getID() << "\'s \"" << list_name << "\" list:" << endl;
	list<string> list_to_print = sb.getContactList(list_name);
	for (list<string>::iterator it = list_to_print.begin(); it != list_to_print.end(); it++)
		cout << *it << endl;

	cout << endl;
}

void printContacts(const sentibyte &sb)
{
	cout << sb.getID() << "\'s contacts:" << endl;
	list<string> contacts = sb.getContacts();
	for (list<string>::iterator it = contacts.begin(); it != contacts.end(); it++)
		cout << *it << endl;

	vector<string> contact_list_names = sb.getContactListNames();
	for (vector<string>::iterator it = contact_list_names.begin(); it != contact_list_names.end(); it++)
	{
		cout << "\"" << *it << "\" list:" << endl;
		list<string> list_to_print = sb.getContactList(*it);
		for (list<string>::iterator list_it = list_to_print.begin(); list_it != list_to_print.end(); list_it++)
			cout << *list_it << endl;
	}

	cout << endl;
}

void printStrangers(const sentibyte &sb)
{
	cout << sb.getID() << "\'s strangers:" << endl;
	list<string> sb_strangers = sb.getStrangers();
	for (list<string>::iterator it = sb_strangers.begin(); it != sb_strangers.end(); it++)
		cout << *it << endl;

	cout << endl;
}

void giveTraits(vector<sb_ptr> &sb_vec)
{
	for (vector<sb_ptr>::iterator it = sb_vec.begin(); it != sb_vec.end(); it++)
	{
		(*it)->addTrait("positivity", value_state(.1f, .9f));
		(*it)->addTrait("energy", value_state(.1f, .9f));
		(*it)->addTrait("intelligence", value_state(.1f, .9f));
		(*it)->addTrait("stamina", value_state(.1f, .9f));
		(*it)->addTrait("sociability", value_state(.1f, .9f));
		(*it)->addTrait("volatility", value_state(.1f, .9f));
		(*it)->addTrait("gullability", value_state(.1f, .9f));
		(*it)->addTrait("intellectual", value_state(.1f, .9f));
	}
}

int main()
{
	jep::init();

	population_ptr test_population(new population);

	vector<sb_ptr> sb_vec;

	sb_vec.push_back(sb_ptr(new sentibyte("Joe Pollack", test_population)));
	sb_vec.push_back(sb_ptr(new sentibyte("Carolyn Pollack", test_population)));
	sb_vec.push_back(sb_ptr(new sentibyte("Alex Rost", test_population)));
	sb_vec.push_back(sb_ptr(new sentibyte("Derek Lariviere", test_population)));

	int others = 8;
	for (int i = 0; i < others; i++)
	{
		string random_name = generateID("random");
		sb_vec.push_back(sb_ptr(new sentibyte(random_name, test_population)));
	}
		
	giveTraits(sb_vec);

	string frag_shader_path = "fragment_shader.glsl";
	string vertex_shader_path = "vertex_shader.glsl";

	display_handler display_context("Sentibytes", frag_shader_path, vertex_shader_path);

	if (display_context.getErrors() == true)
	{
		display_context.printErrors();
		return 0;
	}

	key_handler keystates;
	sb_group geometry_group;

	for (vector<sb_ptr>::iterator it = sb_vec.begin(); it != sb_vec.end(); it++)
		geometry_group.addSBGeometry(*it);
	

	glfwSetTime(0);

	std::ofstream log_file;

	cout << sb_vec.size() << endl;

	do
	{
		glfwPollEvents();

		KEYRETURN returned_key = keystates.checkKeys(display_context);

		display_context.render(geometry_group);

		for (vector<sb_ptr>::iterator it = sb_vec.begin(); it != sb_vec.end(); it++)
			(*it)->fluctuateTraits();

	} while (glfwGetKey(display_context.getWindow(), GLFW_KEY_ESCAPE) != GLFW_PRESS &&
		!glfwWindowShouldClose(display_context.getWindow()));

	return 0;
}