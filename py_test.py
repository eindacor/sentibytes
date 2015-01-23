from sb_fileman import getTruth, cleanup, readSB
from sb_sentibyte import createRandomSBs

sb_list = createRandomSBs(5, getTruth())

info = list()

for sb_ID in sb_list:
    sb = readSB(sb_ID)
    info += sb.getInfo()
    
print info
cleanup()