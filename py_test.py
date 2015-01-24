from sb_fileman import getTruth, cleanup, readSB
from sb_sentibyte import createRandomSBs

ID_list = createRandomSBs(5, getTruth())
sb_list = [readSB(ID) for ID in ID_list]

new_ID_list = [str(sb) for sb in sb_list]
print new_ID_list

sb_list = list()

print new_ID_list

cleanup()