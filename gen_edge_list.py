from utils.cfg_extractor import *

import sys, os



def main():


    inputfile = sys.argv[1]
    rootdir    = sys.argv[2]

    basename = os.path.basename(inputfile)

    outdir = os.path.join(rootdir, basename)

    try:
        os.mkdir(outdir, 0o755)
    except OSError as err:
        print(err)

    php_ext = PHPExtractor()

    php_xml_dom_obj = php_ext.parse(inputfile)
    php_xml_dom = php_xml_dom_obj.analyze()

    name, xml = php_xml_dom[0]
    main = xml['main']
    out_edge_list(main['edge_list'], os.path.join(outdir, f"edge.nx"))





if __name__ == "__main__":
    sys.exit(main())













