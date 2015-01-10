from sb_parser import traitsFromConfig, traitsFromFile
from datetime import datetime

current = datetime.now()

time_string = ''

time_string += str(current.year)
time_string += str(current.month)
time_string += str(current.day)
time_string += str(current.hour)
time_string += str(current.minute)

print time_string
