class randomThing_thing(object):
    number = 5

class randomThing_other(object):
    
    def __init__(self, thing):
        self.stored_thing = thing
    
source_thing = randomThing_thing()

first = randomThing_other(source_thing)
second = randomThing_other(source_thing)

print first.stored_thing
print second.stored_thing