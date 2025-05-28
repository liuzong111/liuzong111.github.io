# XML Parsing Performance Comparison (DOM vs SAX) with English Pseudocode
import xml.sax
from xml.dom.minidom import parse
from datetime import datetime

# ===================== DOM PARSER =====================
'''
FUNCTION dom_parse():
    INIT result dictionary for three ontologies
    TRY:
        LOAD XML document
        GET all <term> elements
        FOR EACH term IN terms:
            TRY:
                EXTRACT namespace, name, id
                COUNT is_a elements
                IF current is_a count > stored maximum FOR this ontology:
                    UPDATE result entry
            HANDLE ERRORS for individual terms
        RETURN result
    HANDLE GLOBAL ERRORS
'''


def dom_parse():
    result = {"biological_process": ("", "", 0), "molecular_function": (
        "", "", 0), "cellular_component": ("", "", 0)}
    try:
        doc = parse("go_obo.xml")
        terms = doc.getElementsByTagName("term")
        for term in terms:
            try:
                ns = term.getElementsByTagName(
                    "namespace")[0].firstChild.nodeValue.strip()
                name = term.getElementsByTagName(
                    "name")[0].firstChild.nodeValue.strip()
                term_id = term.getElementsByTagName(
                    "id")[0].firstChild.nodeValue.strip()
                isa_count = len(term.getElementsByTagName("is_a"))

                if ns in result and isa_count > result[ns][2]:
                    result[ns] = (name, term_id, isa_count)
            except Exception as e:
                print(f"DOM Error parsing term: {e}")
                continue
        return result
    except Exception as e:
        print(f"DOM Parse failed: {e}")
        exit()


# ===================== SAX PARSER =====================
'''
CLASS GOHandler EXTENDS ContentHandler:
    INIT:
        result dictionary for three ontologies
        temporary storage variables
        reset_term() method
    
    METHOD reset_term():
        CLEAR temporary variables for new term
    
    EVENT startElement(tag):
        IF tag == is_a: INCREMENT is_a counter
        SET current processing tag
    
    EVENT endElement(tag):
        IF end of term:
            IF valid ontology AND new maximum is_a count:
                UPDATE result
            RESET temporary variables
    
    EVENT characters(content):
        ACCUMULATE content based on current tag
'''


class GOHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.current_data = ""
        self.result = {"biological_process": ("", "", 0), "molecular_function": (
            "", "", 0), "cellular_component": ("", "", 0)}
        self.reset_term()

    def reset_term(self):
        self.name = ""
        self.id = ""
        self.namespace = ""
        self.isa_count = 0

    def startElement(self, tag, attrs):
        self.current_data = tag
        if tag == "is_a":
            self.isa_count += 1

    def endElement(self, tag):
        if tag == "term":
            if self.namespace in self.result and self.isa_count > self.result[self.namespace][2]:
                self.result[self.namespace] = (
                    self.name.strip(), self.id.strip(), self.isa_count)
            self.reset_term()

    def characters(self, content):
        if self.current_data == "name":
            self.name += content
        elif self.current_data == "id":
            self.id += content
        elif self.current_data == "namespace":
            self.namespace += content


def sax_parse():
    handler = GOHandler()
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)
    try:
        parser.parse("go_obo.xml")
        return handler.result
    except Exception as e:
        print(f"SAX Parse failed: {e}")
        exit()


# ===================== PERFORMANCE COMPARISON =====================
'''
MAIN PROGRAM:
    RECORD start time for DOM
    RUN dom_parse()
    CALCULATE DOM time
    
    RECORD start time for SAX
    RUN sax_parse()
    CALCULATE SAX time
    
    PRINT formatted results
    COMPARE and DISPLAY performance
'''


def print_result(title, result):
    print(f"\n{title}\n" + "-"*40)
    for ns, (name, id_, count) in result.items():
        print(f"Ontology        : {ns}")
        print(f"Term Name       : {name}")
        print(f"Term ID         : {id_}")
        print(f"Number of is_a  : {count}\n")


if __name__ == "__main__":
    # DOM Processing
    dom_start = datetime.now()
    dom_result = dom_parse()
    dom_time = datetime.now() - dom_start

    # SAX Processing
    sax_start = datetime.now()
    sax_result = sax_parse()
    sax_time = datetime.now() - sax_start

    # Output Results
    print_result("GO Term Results by Ontology (DOM)", dom_result)
    print_result("GO Term Results by Ontology (SAX)", sax_result)

    # Performance Comparison
    print("[Performance Comparison]")
    print(f"DOM Time: {dom_time.total_seconds():.3f}s")
    print(f"SAX Time: {sax_time.total_seconds():.3f}s")

    if dom_time < sax_time:
        print("DOM is faster than SAX")
    else:
        print("SAX is faster than DOM")
