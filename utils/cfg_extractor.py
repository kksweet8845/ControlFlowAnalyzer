import xml.etree.ElementTree as ET
from xml.etree import ElementTree
import re
import sys
import json
import os




class PHPOpcodeXMLDOM:
    def __init__(self, tree):
        self.tree = tree


    def analyze(self):
        root = self.tree.getroot()
        
        files = root

        files_xml = []

        for file in files:
            name = file.get('path')
            xml = self.analyze_file(file)

            files_xml.append((name, xml))

        return files_xml

            

    def analyze_file(self, filexml):

        main    = filexml.find("Main")
        fns     = filexml.iter('Function')
        classes = filexml.iter('Classes')

        main_cfg = self._ana_main(main)
        xml = {}
        xml['main'] = {
            'name' : 'main',
            'edge_list' : main_cfg
        }

        xml['functions'] = self._ana_fns(fns)

        return xml


    def _ana_main(self, mainxml):

        # Only analyze basic block

        basicblocks = mainxml.iter('BasicBlock')
        cfg_map = []

        for bb in basicblocks:
            edges, fcall = self._ana_bb(bb)
            cfg_map.append((edges, fcall))

        return cfg_map

    def _ana_fns(self, fns):

        fns_cfg_map = []
        for fn in fns:
            fn_cfg_map = self._ana_fn(fn)
            fns_cfg_map.append(fn_cfg_map)

        return fns_cfg_map

    def _ana_fn(self, fnxml):

        fn_name = fnxml.get("name")
        bbs = fnxml.iter("BasicBlock")

        cfg_map = []
        for bb in bbs:
            edges, fcall = self._ana_bb(bb)
            cfg_map.append((edges, fcall))

        return {
            'name' : fn_name,
            'edge_list' : cfg_map
        }

    def _ana_opcode(self, opcodes):

        fcall = []
        for opcode in opcodes:
            if opcode.get("codeStr") == "INIT_FCALL_BY_NAME":
                op2 = opcode.get("op2_const")
                op2 = re.sub("&quot;", "", op2)
                
                fcall.append(op2)

        return fcall

    def _ana_bb(self, bb):
        cur_id = bb.get("id")
        _from = bb.find('From')
        _to   = bb.find('To')

        from_list = []
        to_list   = []

        edges = []

        for _fref in _from.iter("Ref"):
            from_list.append(_fref.get("bbid"))

        for _tref in _to.iter("Ref"):
            to_list.append(_tref.get("bbid"))

        # for bbid in from_list:
        #     edges.append((bbid, cur_id))

        for bbid in to_list:
            edges.append((cur_id, bbid))

        # analyze opcodes
        fcall = self._ana_opcode(bb.iter("Opcode"))

        return edges, fcall



class PHPExtractor:
    def __init__(self):
        self.tree = None
        self.root = None


    def parse(self, path):
        tree = ET.parse(path)
        return PHPOpcodeXMLDOM(tree)


def out_edge_list(edge_list, outname):

    out = open(outname, "w")
    for edges, fcall in edge_list:
        for edge in edges:
            out.write(f"{edge[0]} {edge[1]}\n")
    out.close()





if __name__ == "__main__":


    filename = sys.argv[1]
    php_ext = PHPExtractor()
    
    php_xml_dom_ = php_ext.parse(filename)
    
    files = php_xml_dom_.analyze()

    out_file = open(f"{os.path.basename(filename)}.log", "w")


    for filename, php_xml_dom in files:
        out_file.write(f"filename: {filename}\n")
        # main edge list
        main = php_xml_dom['main']
        out_file.write("#"*60 + "\n")
        out_file.write(f"Name : {main['name']}\n")
        for edges, fcall in main['edge_list']:
            out_file.write(f"fcall: {fcall}\n")
            for edge in edges:
                out_file.write(f"Edge : {edge[0]} -> {edge[1]}\n")

        # function edge list
        fns = php_xml_dom['functions']

        for fn in fns:
            out_file.write("#" * 60 + "\n")
            out_file.write(f"Name: {fn['name']}\n")
            for edges, fcall in fn['edge_list']:
                out_file.write(f"fcall: {fcall}\n")
                for edge in edges:
                    out_file.write(f"Edge : {edge[0]} -> {edge[1]}\n")






















