#include "sb_perception.h"
#include "sb_sentibyte.h"

perception::perception(string other, const sentibyte &owner_sb)
{
	owner_ID = owner_sb.getID();
	other_ID = other;
	broadcasts_observed = 0;
	cycles_observed = 0;
	rumors_heard = 0;
	memories_counted = 0;

	avgContainer overall_rating(owner_sb["regard"]["current"], 0);
}

void addInteraction(interaction observed, const sentibyte &self, bool isRumor)
{

}

void perception::addInstance(unsigned short weight)
{
	float rating = boundsCheck(getOverallRating() + float(weight));
	avg_instance_rating.addValue(rating);
	overall_rating.addValue(rating);
}