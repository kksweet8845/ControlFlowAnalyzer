import re
from utils.cfg_extractor import *
import os




class CFIExecutor:

    def __init__(self, runtime_filepath, xml_dir):
        self.php_cfg_ext = PHPExtractor()
        self.cfg_dict = {}
        self.xml_dir = xml_dir
        self.runtime_flow = None
        self.bbid_mapping = {}
        self.bbid_max = -1

        self.read_runtime(runtime_filepath)

    def dump_edge_list(self, outpath):

        entry_dir = self.runtime_flow['entry_file']

        entry_dir = re.sub(r"\.", "_", entry_dir)

        outdir = os.path.join(outpath, entry_dir)
        
        if not os.path.exists(outdir):
            os.mkdir(outdir, 0o755)
        
        outfile = os.path.join(outdir, "edge.nx")
        print(outfile)
        
        try:
            file = open(outfile, 'w')
        except IOError as e:
            print("I/O error{0} : {1}".format(e.errno, e.strerror))

        for context_path in self.cfg_dict.keys():
            # main
            if context_path == 'extra_edges':
                for edge in self.cfg_dict[context_path]:
                    file.write(f"{edge[0]} {edge[1]}\n")
                continue

            cfg = self.cfg_dict[context_path]
            
            main = cfg['main']
            for edge in main['mapped_edge_list']:
                file.write(f"{edge[0]} {edge[1]}\n")

            #function
            for fn in cfg['functions']:
                for edge in fn['mapped_edge_list']:
                    file.write(f"{edge[0]} {edge[1]}\n")

            # classes
            for _class in cfg['classes']:
                for fn in _class['functions']:
                    for edge in fn['mapped_edge_list']:
                        file.write(f"{edge[0]} {edge[1]}\n")


        file.close()

    def read_runtime(self, filepath):

        runtime_flow = {}

        parsed_cfg = []

        file = open(filepath, 'r')
        lines = file.readlines()

        del lines[0]
        del lines[1]

        entry_file = lines[0]
        runtime_log = lines[1:]

        runtime_flow['entry_file'] = None

        # template = {
        #     'context_path' : None,
        #     'context'      : None,
        #     'bbid'         : None
        # }
        ptr = runtime_flow['sequence'] = []

        for i, line in enumerate(runtime_log):

            # print(tuple(line.split(' ')))
            context_bb, context_path = tuple(line.split(' '))
            
            context_path = re.sub('/', '_', context_path)
            context_path = re.sub('\n', '', context_path)
            org_context_path = context_path
            if i == 0:
                runtime_flow['entry_file'] = org_context_path

            context_path += ".xml"
            context_abs_path = os.path.join(self.xml_dir, context_path)

            if org_context_path not in parsed_cfg:
                self.add_cfg(context_abs_path, org_context_path)
                parsed_cfg.append(org_context_path)
                self.ctor_cfg(org_context_path)

            context, bbid = self._context_bb_split(context_bb)
            bbid = int(bbid)

            elt = {
                'context_path' : org_context_path
            }

            if self.is_main(context):
                elt['context'] = 'main'
                elt['bbid']    = bbid + self.cfg_dict[org_context_path]['main']['lowb'] 
            else:
                elt['context'] = context
                elt['bbid']    = bbid + self.find_lowb(org_context_path, context)

            ptr.append(elt)

        extra_edges = self.connc_graph(ptr)
        self.cfg_dict['extra_edges'] = extra_edges
        self.runtime_flow = runtime_flow

    def connc_graph(self, sequence):
        extra_edges = self._connc_graph(sequence)
        return extra_edges
    
    def _connc_graph(self, runtime_seq):

        context_stack = []
        cur_context_path = None
        cur_context      = None
        extra_edges = []
        last_context_path = last_context = last_bbid = None


        prev_bbid = last_bbid
        for i in range(len(runtime_seq)):

            context_path = runtime_seq[i]['context_path']
            context      = runtime_seq[i]['context']
            bbid         = runtime_seq[i]['bbid']

            if cur_context_path == None and cur_context == None: # initial
                cur_context_path = context_path
                cur_context = context
                # seq.append(bbid)
            elif cur_context_path == context_path and cur_context == context: # still inside same function
                # seq.append(bbid)
                pass
            elif cur_context_path != context_path or cur_context != context: # find uncod jump
                if last_context_path != None and last_context != None and \
                    last_context_path == context_path and \
                    last_context == context: # back to previous context
                    extra_edges.append((prev_bbid, bbid))
                    context_stack.pop()
                    cur_context_path = context_path
                    cur_context = context
                else: # another context
                    context_stack.append({
                        'context_path' : cur_context_path,
                        'context'      : context,
                        'bbid'         : bbid
                    })
                    extra_edges.append((prev_bbid, bbid))
                    last_context_path = cur_context_path
                    last_context      = cur_context
                    last_bbid         = bbid

            prev_bbid = bbid

        return extra_edges



    def find_lowb(self, context_path, context):

        _is_class = self.is_class(context)

        if _is_class:
            # print(context_path)
            classes = self.cfg_dict[context_path]['classes']
            # print(classes)
            class_name, class_fnname = tuple(context.split("::"))
            print(class_name, class_fnname)
            for _class in classes:
                if _class['name'] == class_name or _class['name'] == None:
                    for fn in _class['functions']:
                        if fn['name'] == context:
                            return fn['lowb']
        else:
            fns = self.cfg_dict[context_path]['functions']
            for fn in fns:
                if fn['name'] == context:
                    return fn['lowb']

        return None

    def ctor_cfg(self, context_path):

        cur_cfg = self.cfg_dict[context_path]

        
        main = cur_cfg['main']
        
        edges = main['edge_list']

        mapped_edges, lowb, upb = self.gen_edge_list(edges)
        main['mapped_edge_list'] = mapped_edges
        main['lowb'] = lowb
        main['upb']  = upb

        fns = cur_cfg['functions']

        for fn in fns:
            edges = fn['edge_list']
            mapped_edges, lowb, upb = self.gen_edge_list(edges)
            fn['mapped_edge_list'] = mapped_edges
            fn['lowb'] = lowb
            fn['upb']  = upb

        classes = cur_cfg['classes']

        for _class in classes:
            for fn in _class['functions']:
                edges = fn['edge_list']
                mapped_edges, lowb, upb = self.gen_edge_list(edges)
                fn['mapped_edge_list'] = mapped_edges
                fn['lowb'] = lowb
                fn['upb']  = upb

            


    def gen_edge_list(self, edges):
        edge_list = []

        _max = -1

        for elt in edges:
            edges = elt['edges']
            for edge in edges:
                _from, _to = int(edge[0]), int(edge[1])
                t_edge = list([int(edge[0]), int(edge[1])])
                edge_list.append(t_edge)

                if _from > _max:
                    _max = _from
                
                if _to > _max:
                    _max = _to

        lower_bound = self.bbid_max + 1 + 0
        upper_bound = self.bbid_max + 1 + _max

        for edge in edge_list:
            edge[0] = edge[0] + lower_bound
            edge[1] = edge[1] + lower_bound

        self.bbid_max = upper_bound    
        
        return edge_list, lower_bound, upper_bound



    def _context_bb_split(self, context_bb):

        print(context_bb)
        ext_obj = re.search(r"^([$0-9a-zA-Z:_]+)_([0-9]+)", context_bb)

        context = ext_obj.group(1)
        bb      = ext_obj.group(2)
        print(context, bb)
        return context, bb

    def is_main(self, _str):
        return re.match(r"\$_main", _str) != None

    def is_class(self, _str):
        return re.match(r"[a-zA-Z0-9_]+::[a-zA-Z0-9_]+", _str) != None

    def add_cfg(self, path, org_path):

        if path in self.cfg_dict.keys():
            return
        cfg = self.parse_cfg(path)
        self.cfg_dict[org_path] = cfg[1]



    def parse_cfg(self, path):
        php_xml_dom = self.php_cfg_ext.parse(path)
        cfgs = php_xml_dom.analyze()
        cfg = cfgs[0]
        return cfg
        





if __name__ == "__main__":

    path = "/home/nobertai/repo/ControlFlowAnalyzer/test-data/php-log/0.pb.log"
    opcode_dir = "/home/nobertai/repo/ControlFlowAnalyzer/pure-data/php-opcode"
    cfexe = CFIExecutor(path, opcode_dir)

    outdir = "/home/nobertai/repo/ControlFlowAnalyzer/data"
    cfexe.dump_edge_list(outdir)






