import os
from unicode_map import number_map, measure_map, rest_map
import music21 as m
from musicxml.parser.parser import _parse_node
from musicxml import *

import docx
import docx.document
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

import xml.etree.ElementTree as ET
import xml

from zipfile import ZipFile
import math

def unicode_to_char(unicode_string:str):
    return chr(int(unicode_string, 16))

class Barline:
    def __init__(self, ):
        self.repeat:bool = False
        self.type:str = 'simple' # ligth, heavy or double

class Note:  
    def __init__(self, note:XMLNote, division:int, key:str):
        self.unicode:list[str] = ['']
        self.string = ''
        self.base_note = '' # solfage
        self.dots = 0 # 1,2,3
        self.dot_position = 'a' # a = above, b = below
        self.duration = note.get_children_of_type(XMLDuration)[0].value_
        self.division = division
        self.note = note
        self.key = key

        # Rest
        if note.get_children_of_type(XMLRest):
            frac, whole = math.modf(self.duration/self.division)
            self.string = '0'
            try:
                if frac > 0 and whole < 1:
                    self.string += '-' + 'l'*int(math.log(int(1/frac),2))
                # TODO add rest unicode
                if whole > 1:
                    if frac > 0:
                        # notes.append(measure_map['dot'])
                        self.string += ' + dot'

                    # More than one whole note
                    # for x in range(1, int(whole)):
                        # notes.append(rest_map[self.string])
            except:
                print('Rest not found')
        # Actual note
        else:
            self._note_to_string()


    def _note_to_string(self):
        """
        Convert XMLNote
        """
        pitch:XMLPitch = self.note.get_children_of_type(XMLPitch)[0]
        step = pitch.get_children_of_type(XMLStep)[0].value_
        octave = pitch.get_children_of_type(XMLOctave)[0].value_
        duration = self.note.get_children_of_type(XMLDuration)[0].value_
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
        
        self._note_to_unicode(f'{step}{alter}{octave}', duration)

    def _note_to_unicode(self, note:str, duration:int) -> list[str]:
        """
        Convert XMLNote to the correct jianpu string with length
        """
        n = m.note.Note(note)
        k = m.key.Key(self.key)
        base_note = m.note.Note(k.getScale('major').pitches[0].name)

        interval = m.interval.Interval(base_note, n)
        distance = abs(math.floor(interval.semitones / 12)) * interval.direction

        self.base_note = k.getScale().getScaleDegreeFromPitch(n)

        if self.base_note == None:
            raise ValueError('Note not in key signature')
        if distance > 3 or distance < -3:
            raise ValueError('Note not in disatonic range')

        self.string = str(self.base_note)
        match distance:
            case _ if distance > 0:
                self.string += '-a'
                self.string += 'd'* abs(distance)
            case _ if distance < 0:
                self.string += '-u'
                self.string += 'd'*abs(distance)
            case _ if distance == 0:
                self.string += ''

        return self._add_duration()
    
    def _add_duration(self) -> list[str]:
        """
        Add the duration to the note string
        """
        frac, whole = math.modf(self.duration/self.division)
        characters = []

        if frac > 0 and whole < 1:
            if not self.string.__contains__('-'):
                self.string += '-'
            self.string += 'l'*int(math.log(int(1/frac),2))
        characters.append(number_map[self.string])
        if frac == 0.5 and whole >= 1:
            characters.append(measure_map['dot'])
        if whole > 1:
            for x in range(1, int(whole)):
                characters.append(measure_map['dash'])

        self.unicode = characters
    
class Measure:
    def __init__(self, measure:XMLMeasure, division:int=4, time:tuple[int,int]=(4,4), key:str='C'):
        self.start_bar:Barline = None
        self.end_bar:Barline = Barline()
        self.division:int = division
        self.time:tuple[int,int] = time # (beats, beat-type)
        self.key:str = key
        self.notes = []

        self._convert_measure(measure)

    def _convert_barline(self, barline:XMLBarline):
        new_barline = Barline()
        if barline.get_children_of_type(XMLRepeat):
            new_barline.repeat = True
            new_barline.type = 'bold'
            match barline.get_children_of_type(XMLRepeat)[0].to_string().split('"')[1]:
                case 'forward':
                    self.start_bar = new_barline
                    # measure.start_bar = measure_map['bar_lines']['repeat_forward']
                case 'backward':
                    self.end_bar = new_barline
                    # measure.end_bar = measure_map['bar_lines']['repeat_backward']
                case _:
                    raise ValueError('Invalid repeat type')
                    # measure.end_bar = measure_map['bar_lines']['bold_double']

            # if previous is not None:
            #     for x in previous.get_children_of_type(XMLBarline):
            #         if x.get_children_of_type(XMLRepeat)[0].to_string().split('"')[1] == 'backward':
            #             measure.start_bar = measure_map['bar_lines']['repeat_both']
            #             break
        else:
            new_barline.type = "simple"
            self.end_bar = new_barline

    def _convert_key_signature(self, key_signature:XMLKey)->str:
        """
        Converts the key signature
        """
        self.key = (str)(m.key.KeySignature(key_signature.get_children_of_type(XMLFifths)[0].value_).asKey()).split(' ')[0]
        # try:
        #     return measure_map['key_signatures'][key]
        # except:
        #     print('Key signature not found, defaulting to D')
        #     return measure_map['key_signatures']['D']

    def _convert_time_signature(self,time_signature:XMLTime)->str:
        """
        Converts the time signature
        """
        # time_signature = time_signature.get_children_of_type(XMLBeats)[0].value_+'/'+time_signature.get_children_of_type(XMLBeatType)[0].value_
        # try:
        #     return measure_map['time_signatures'][time_signature]
        # except:
        #     print('Time signature not found, defaulting to 4/4')
        #     return measure_map['time_signatures']['4/4']
        
        self.time = (time_signature.get_children_of_type(XMLBeats)[0].value_, time_signature.get_children_of_type(XMLBeatType)[0].value_)

    def _convert_attributes(self, attributes:XMLAttributes)->tuple[str, str]:
        for child in attributes.get_children():
            if isinstance(child, XMLKey):
                self._convert_key_signature(key_signature=child)
            if isinstance(child, XMLTime):
                self._convert_time_signature(time_signature=child)
            if isinstance(child, XMLDivisions):
                self.division = int(child.value_)

    def _convert_measure(self, measure:XMLMeasure | None):
        
        for child in measure.get_children():
            if isinstance(child, XMLNote):
                # Skip erverything that is not in the first voice and staff
                if (child.get_children_of_type(XMLVoice)[0].value_ != '1'):
                    continue
                if len(child.get_children_of_type(XMLStaff)) != 0 and (child.get_children_of_type(XMLStaff)[0].value_ != 1) :
                    continue
                self.notes.append(Note(child, self.division, self.key))
            if isinstance(child, XMLAttributes):
                self._convert_attributes(child)
            if isinstance(child, XMLBarline):
                self._convert_barline(child)

class Jianpu:
    def __init__(self, doc: ET):
        self.title = 'Unknown'
        self.composer = 'Unknown'
        self.measures:list[Measure] = []
        self.division:int = None
        self.time:tuple[int,int] = (4,4) # (beats, beat-type)
        self.filename:str = None
        self.key:str = 'C'
        self.xml_doc:ET = doc
        self.mxl_doc:XMLScorePartwise = _parse_node(doc)
        self.docx:docx.document.Document = docx.Document(os.path.abspath('jianpu/sample.docx'))

        self._parse()
        if self.filename is None:
            self.filename = self.title.strip().replace(' ', '_')

    def from_file_path( filepath: str) -> 'Jianpu':
        with ZipFile(filepath, 'r') as zipObj:
            xml_string = zipObj.read('score.xml').decode('utf-8')
        
        j = Jianpu(ET.fromstring(xml_string))
        j.filename = os.path.basename(filepath)

        return j
    
    def from_string(xml_string: str) -> 'Jianpu':
        return Jianpu(ET.fromstring(xml_string))
    
    def _add_jianpu_paragraph(self, string:str, text_size:int=16):
        paragraph = self.docx.add_paragraph(string)
        run = paragraph.runs[0]
        run.font.name = 'SimpErhuFont'
        run.font.size = Pt(text_size)
    
    def _parse(self):
        work_title = self.xml_doc.find('./work/work-title')
        creator = self.xml_doc.find('./identification/creator')

        self.title = work_title.text if work_title is not None else 'Unknown title'
        self.composer = creator.text if creator is not None else 'Unknown creator'

        parts:list[XMLPart] = self.mxl_doc.get_children_of_type(XMLPart)
        measures = parts[0].get_children_of_type(XMLMeasure)
        for measure in measures:
            if self.division is None:
                self.measures.append(Measure(measure))
                self.division = self.measures[-1].division
                self.key = self.measures[-1].key
                self.time = self.measures[-1].time
            else:
                self.measures.append(Measure(measure, self.division, self.time, self.key))

    def _get_jianpu_string(self) -> str:
        """
        Get the jianpu string from the measures
        """
        string = ''
        for i, measure in enumerate(self.measures):
            if measure.start_bar is not None:
                if self.measures[i-1].end_bar.repeat is True:
                    string[-1] = unicode_to_char(measure_map['bar_lines']['repeat_both'])
                else:
                    string += unicode_to_char(measure_map['bar_lines']['repeat_forward'])
            for note in measure.notes:
                string += ''.join([unicode_to_char(i) for i in note.unicode])
            if measure.end_bar is not None:
                string += unicode_to_char(measure_map['bar_lines'][measure.end_bar.type])
        return string
    
    def save_docx(self, path:str):
        self.docx.paragraphs[0].text = self.docx.paragraphs[0].text.replace('Song Title', self.title)
        self.docx.paragraphs[1].text = self.docx.paragraphs[1].text.replace('Composer', self.composer)

        out = self._get_jianpu_string()

        self._add_jianpu_paragraph(string=out)
        self.docx.save(path)

if __name__ == '__main__':
    j: Jianpu = Jianpu.from_file_path(filepath='mxl/oogway.mxl')
    j.save_docx(path='docx/new2.docx')

