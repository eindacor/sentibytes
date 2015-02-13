#include <iostream>
#include "sb_sentibyte.h"

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

int main()
{
	jep::init();

	population_ptr test_population(new population);

	sentibyte joe("Joe Pollack", test_population);
	sentibyte carolyn("Carolyn Pollack", test_population);
	sentibyte alex("Alex Rost", test_population);
	sentibyte derek("Derek Lariviere", test_population);
	sentibyte doug("Doug Random", test_population);
	sentibyte fred("Fred Random", test_population);

	test_population->addMember(derek.getID());
	test_population->addMember(joe.getID());
	test_population->addMember(carolyn.getID());
	test_population->addMember(doug.getID());
	test_population->addMember(fred.getID());

	joe.addTrait("positivity", value_state(.1f, .9f));
	carolyn.addTrait("positivity", value_state(.25f, .5f, .75f));

	joe.addContactList("friends");
	joe.addContactList("wife");
	joe.addToContactList(carolyn.getID(), "friends");
	joe.addToContactList(carolyn.getID(), "wife");
	joe.addToContactList(derek.getID(), "friends");
	joe.addToContactList(alex.getID(), "friends");
	joe.addToContactList(fred.getID(), "friends");
	joe.addToContactList(doug.getID(), "friends");

	printStrangers(joe);
	printContacts(joe);
	joe.removeFromContacts(doug.getID());
	printContacts(joe);
	joe.removeFromContactList(fred.getID(), "friends");
	printContacts(joe);
	printStrangers(joe);

	return 0;
}