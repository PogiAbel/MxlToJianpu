import musicxml
from musicxml.parser.parser import _parse_node
from musicxml import *
from docx import Document
from docx.shared import Pt
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import xml

# Get xml file
# with ZipFile('mxl/sample.mxl', 'r') as zipObj:
#     xml_string = zipObj.read('score.xml').decode('utf-8')

# xml = ET.fromstring(xml_string)

# mxl:XMLScorePartwise  = _parse_node(xml)

# Create a new Document
path = "docx/jianpu.docx"
doc = Document(path)
p_style = doc.styles['Normal']

paragraph = doc.add_paragraph(doc.paragraphs[-1].text)
run = paragraph.runs[0]
run.font.name = 'SimpErhuFont'
run.font.size = Pt(16)


doc.save("docx/new.docx")