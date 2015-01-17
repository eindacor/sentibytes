class first(object):
    def __init__(self, thing):
        self.first_thing = thing
        
random_list = [1, 2, 3, 4]

first_object = first(random_list)
print first_object.first_thing

random_list.append(5)
print first_object.first_thing

second = {1: 'a', 2: 'b'}
print len(second)