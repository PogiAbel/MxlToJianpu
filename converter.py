import xml
import musicxml

# unicode string of the characters
# Number structure: number + a(above)/u(under) + number of dots in d + number of lines in l
# Example: 1-add-ll = 1 above 2 dots and 2 lines under it
# Example: 7-ud = 7 under one dot and no lines

char_map: dict ={
    '0':'0030',
    '1':'0031',
    '2':'0032',
    '3':'0033',
    '4':'0034',
    '5':'0035',
    '6':'0036',
    '7':'0037',
    '1-ud':'00c0',
    '2-ud':'00c1',
    '3-ud':'00c2',
    '4-ud':'00c3',
    '5-ud':'00c4',
    '6-ud':'00c5',
    '7-ud':'00c6',
    '1-udd':'00b9',
    '2-udd':'00ba',
    '3-udd':'00bb',
    '4-udd':'00bc',
    '5-udd':'00bd',
    '6-udd':'00be',
    '7-udd':'00bf',
    '1-uddd':'00b2',
    '2-uddd':'00b3',
    '3-uddd':'00b4',
    '4-uddd':'00b5',
    '5-uddd':'1e06',
    '6-uddd':'00b7',
    '7-uddd':'00b8',
}