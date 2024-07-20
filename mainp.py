import docx.document
import musicxml
from musicxml.parser.parser import _parse_node
from musicxml import *
import docx
from docx.shared import Pt
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import xml
from converter import char_map

def add_jianpu_paragraph(string:str, doc:docx.document.Document, text_size:int=16):
    paragraph = doc.add_paragraph(string)
    run = paragraph.runs[0]
    run.font.name = 'SimpErhuFont'
    run.font.size = Pt(text_size)

def unicode_to_char(hex_string:str):
    return chr(int(hex_string, 16))

# Get xml file
# with ZipFile('mxl/sample.mxl', 'r') as zipObj:
#     xml_string = zipObj.read('score.xml').decode('utf-8')

# xml = ET.fromstring(xml_string)

# mxl:XMLScorePartwise  = _parse_node(xml)

# Create a new Document
path = "docx/new.docx"
doc = docx.Document(path)

new_string = ''.join([unicode_to_char(x) for x in char_map.values()])
add_jianpu_paragraph(new_string, doc)
doc.save("docx/new.docx")