import musicxml
from musicxml.parser.parser import _parse_node
from musicxml import *
import musicscore
from docx import Document
from zipfile import ZipFile
import xml.etree.ElementTree as ET

# Get xml file
with ZipFile('mxl/sample.mxl', 'r') as zipObj:
    xml_string = zipObj.read('score.xml').decode('utf-8')

xml = ET.fromstring(xml_string)

mxl:XMLScorePartwise  = _parse_node(xml)
print(mxl.get_children()[6].name)