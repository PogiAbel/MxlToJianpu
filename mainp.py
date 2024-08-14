import docx.document
import musicxml
from musicxml.parser.parser import _parse_node
from musicxml import *
import docx
from docx.shared import Pt
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import xml
from converter import number_map, measure_map
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt
import music21

def add_jianpu_paragraph(string:str, doc:docx.document.Document, text_size:int=16):
    paragraph = doc.add_paragraph(string)
    run = paragraph.runs[0]
    run.font.name = 'SimpErhuFont'
    run.font.size = Pt(text_size)
    

def unicode_to_char(unicode_string:str):
    return chr(int(unicode_string, 16))

# Get xml file
with ZipFile('mxl/sample.mxl', 'r') as zipObj:
    xml_string = zipObj.read('score.xml').decode('utf-8')

xml = ET.fromstring(xml_string)

mxl:XMLScorePartwise  = _parse_node(xml)



mxl.get_children_of_type

# Get notes
# for child in mxl.get_children():
#     if isinstance(child, XMLPart):
#         for measure in child.get_children():
#             for note in measure.get_children():
#                 if isinstance(note, XMLNote):
#                     if note.get_children_of_type(XMLRest) == []:
#                         print(note.to_string())

key_signature:XMLFifths | str = mxl.get_children_of_type(XMLPart)[0].get_children()[0].get_children_of_type(XMLAttributes)[0].get_children_of_type(XMLKey)[0].get_children_of_type(XMLFifths)[0]
key_signature = (str)(music21.key.KeySignature(key_signature.value_).asKey()).split(' ')[0]

time: XMLTime | str = mxl.get_children_of_type(XMLPart)[0].get_children()[0].get_children_of_type(XMLAttributes)[0].get_children_of_type(XMLTime)[0].get_children()
time = time[0].value_+'/'+time[1].value_

def note(node:XMLNote):
    pass


# Create a new Document
path = "docx/sample.docx"
doc = docx.Document(path)

new_chars:list = []

try:
    new_chars.append(measure_map['key_signatures'][key_signature])
except:
    print('Key signature not found, defaulting to D')
    new_chars.append(measure_map['key_signatures']['D'])

try:
    new_chars.append(measure_map['time_signatures'][time])
except:
    print('Time signature not found, defaulting to 4/4')
    new_chars.append(measure_map['time_signatures']['4/4'])

new_string = ''.join(unicode_to_char(char) for char in new_chars)

print(new_string)

add_jianpu_paragraph(new_string, doc)
doc.save("docx/new.docx")