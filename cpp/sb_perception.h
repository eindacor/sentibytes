#ifndef SB_PERCEPTION_H
#define SB_PERCEPTION_H

#include "sb_header.h"

class perception
{
public:
	perception(string other, const sentibyte &owner_sb);
	~perception(){};

	const float getOverallRating() const { return overall_rating.getAverage(); }
	const float getDesiredOffset() const { return avg_desired_offset.getAverage(); }
	const float getInteractionRating() const { return avg_interaction_rating.getAverage(); }
	const float getInstanceRating() const { return avg_instance_rating.getAverage(); }

	void addInteraction(interaction observed, sentibyte &sb, bool isRumor, bool isMemory);
	void addInstance(unsigned short weight);
	const string getOwner() const { return owner_ID; }
	const string getOther() const { return other_ID; }

	const bool operator == (const perception &comparator) const { return (getOverallRating() == comparator.getOverallRating()); }
	const bool operator != (const perception &comparator) const { return (getOverallRating() != comparator.getOverallRating()); }
	const bool operator < (const perception &comparator) const { return (getOverallRating() < comparator.getOverallRating()); }
	const bool operator <= (const perception &comparator) const { return (getOverallRating() <= comparator.getOverallRating()); }
	const bool operator > (const perception &comparator) const { return (getOverallRating() > comparator.getOverallRating()); }
	const bool operator >= (const perception &comparator) const { return (getOverallRating() >= comparator.getOverallRating()); }

	operator float() const { return getOverallRating(); }

private:
	string owner_ID;
	string other_ID;
	signed short broadcasts_observed;
	signed short cycles_observed;
	signed short rumors_heard;
	signed short memories_counted;

	avgContainer overall_rating;
	avgContainer avg_desired_offset;
	avgContainer avg_interaction_rating;
	avgContainer avg_instance_rating;
};

#endif