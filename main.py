import docx.document
import musicxml
from musicxml.parser.parser import _parse_node
from musicxml import *
import docx
from docx.shared import Pt
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import xml
from converter import number_map, measure_map, rest_map
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt
import music21 as m
import math

WRITE_LIST = []
my_key = ''
divison = 0

def add_jianpu_paragraph(string:str, doc:docx.document.Document, text_size:int=16):
    paragraph = doc.add_paragraph(string)
    run = paragraph.runs[0]
    run.font.name = 'SimpErhuFont'
    run.font.size = Pt(text_size)
    
def unicode_to_char(unicode_string:str):
    return chr(int(unicode_string, 16))

def add_duration(note_string:str, duration:int) -> list[str]:
    """
    Given the note string and the duration, return the correct jianpu unicode character and/or added durations in a list
    """
    global divison
    frac, whole = math.modf(duration/divison)
    characters = []

    if frac > 0 and whole < 1:
        if not note_string.__contains__('-'):
            note_string += '-'
        note_string += 'l'*int(math.log(int(1/frac),2))
    characters.append(number_map[note_string])
    if frac == 0.5 and whole >= 1:
        characters.append(measure_map['dot'])
    if whole > 1:
        for x in range(1, int(whole)):
            characters.append(measure_map['dash'])

    return characters

def note_to_unicode(key:str, note:str, duration:int) -> list[str]:
    """
    Convert note text to the correct jianpu unicode characters with length
    """
    n = m.note.Note(note)
    k = m.key.Key(key)
    base_note = m.note.Note(k.getScale('major').pitches[0].name)

    interval = m.interval.Interval(base_note, n)
    distance = abs(math.floor(interval.semitones / 12)) * interval.direction

    solfage = k.getScale().getScaleDegreeFromPitch(n)

    if solfage == None:
        raise ValueError('Note not in key signature')
    if distance > 3 or distance < -3:
        raise ValueError('Note not in disatonic range')

    note_text = str(solfage)
    match distance:
        case _ if distance > 0:
            note_text += '-a'
            note_text += 'd'* abs(distance)
        case _ if distance < 0:
            note_text += '-u'
            note_text += 'd'*abs(distance)
        case _ if distance == 0:
            note_text += ''

    return add_duration(note_text, duration)

def note_to_string(note:XMLNote, duration:int) -> list[str]:
    """
    Convert XMLNote to the correct jianpu string with length
    """
    global my_key
    pitch:XMLPitch = note.get_children_of_type(XMLPitch)[0]
    step = pitch.get_children_of_type(XMLStep)[0].value_
    octave = pitch.get_children_of_type(XMLOctave)[0].value_
    duration = note.get_children_of_type(XMLDuration)[0].value_
    alter = ''
    try:
        alter = (int)(pitch.get_children_of_type(XMLAlter)[0].value_)
        match alter:
            case 1:
                alter = '#'
            case -1:
                alter = 'b'
            case 0:
                alter = ''
    except:
        pass
    
    return note_to_unicode(my_key, f'{step}{alter}{octave}', duration)

def convert_note(note:XMLNote | None):
    global divison, WRITE_LIST
    duration = note.get_children_of_type(XMLDuration)[0].value_

    # Rest
    if note.get_children_of_type(XMLRest):
        frac, whole = math.modf(duration/divison)
        rest_string = '0'
        try:
            if frac > 0 and whole < 1:
                rest_string += '-' + 'l'*int(math.log(int(1/frac),2))
            WRITE_LIST.append(rest_map[rest_string])
            if whole > 1:
                if frac > 0:
                    WRITE_LIST.append(measure_map['dot'])
                for x in range(1, int(whole)):
                    WRITE_LIST.append(rest_map[rest_string])
        except:
            print('Rest not found')
    # Actual note
    else:
        WRITE_LIST += note_to_string(note, duration)

def convert_key_signature(key_signature:XMLKey):
    key:str = (str)(m.key.KeySignature(key_signature.get_children_of_type(XMLFifths)[0].value_).asKey()).split(' ')[0]
    global my_key
    my_key = key
    try:
        WRITE_LIST.append(measure_map['key_signatures'][key])
    except:
        print('Key signature not found, defaulting to D')
        WRITE_LIST.append(measure_map['key_signatures']['D'])

def convert_time_signature(time_signature:XMLTime):
    time_signature = time_signature.get_children_of_type(XMLBeats)[0].value_+'/'+time_signature.get_children_of_type(XMLBeatType)[0].value_
    try:
        WRITE_LIST.append(measure_map['time_signatures'][time_signature])
    except:
        print('Time signature not found, defaulting to 4/4')
        WRITE_LIST.append(measure_map['time_signatures']['4/4'])

def convert_attributes(attributes:XMLAttributes):
    for child in attributes.get_children():
        if isinstance(child, XMLKey):
            convert_key_signature(child)
        if isinstance(child, XMLTime):
            convert_time_signature(child)
        if isinstance(child, XMLDivisions):
            global divison
            divison = int(child.value_)

def convert_measure(measure:XMLMeasure | None):
    if measure is None:
        return
    for child in measure.get_children():
        if isinstance(child, XMLNote):
            convert_note(child)
        if isinstance(child, XMLAttributes):
            convert_attributes(child)
        if isinstance(child, XMLBarline):
            WRITE_LIST.append(measure_map['bar_line'])
    WRITE_LIST.append(measure_map['bar_line'])
    convert_measure(measure.next)

# Get xml file
with ZipFile('mxl/sample.mxl', 'r') as zipObj:
    xml_string = zipObj.read('score.xml').decode('utf-8')

xml = ET.fromstring(xml_string)

mxl:XMLScorePartwise  = _parse_node(xml)

credit_list: list = {}
for credit in mxl.get_children_of_type(XMLCredit):
    type = value = ''
    for child in credit.get_children():
        if isinstance(child, XMLCreditType):
            type = child.value_
        if isinstance(child, XMLCreditWords):
            value = child.value_
    credit_list[type] = value

parts:list[XMLPart] = mxl.get_children_of_type(XMLPart)

for part in parts:
    convert_measure(part.get_children()[0])

# # Create a new Document
path = "docx/sample.docx"
doc = docx.Document(path)

new_string = ''.join(unicode_to_char(char) for char in WRITE_LIST)

add_jianpu_paragraph(new_string, doc)
doc.save("docx/new.docx")