from sb_fileman import getTruth, createRandomSBs, writeSB, readSB, cleanup

sb_list = createRandomSBs(2, getTruth())

sb = sb_list[0]
sb_ID = sb.sentibyte_ID

print sb_ID

writeSB(sb)
copy = readSB(sb_ID)

print copy.sentibyte_ID
cleanup()