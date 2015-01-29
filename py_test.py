from sb_utilities import averageContainer

container = averageContainer()

container.addAverage(50, 2)

print container.average

container.addValue(20)

print container.average

container.addAverage(10, 7)

print container.average

empty_container = averageContainer()

print str(container)
print str(empty_container)