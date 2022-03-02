from utils.cfg_extractor import *

import sys, os
import json
import argparse



def gen_single_file(filepath):
    pass


def gen_edge_from_dir(dir_path, outdir):
    files = os.listdir(dir_path)
    php_ext = PHPExtractor()

    for _file in files:
        filepath = os.path.join(dir_path, _file)

        if os.path.isfile(filepath):
            php_xml_dom_obj = php_ext.parse(filepath)
            php_xml_dom = php_xml_dom_obj.analyze()

            js_str = json.dumps(php_xml_dom, indent=4)

            file = open(os.path.join(outdir, _file), 'w')
            file.write(js_str)
            file.close()





def main():



    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-f", "--file",
                        type=str,
                        help="Specify the file path, only extract from one file")
    parser.add_argument("-d", "--dir",
                        type=str,
                        help="Specify the directory path, extract from a directory")

    parser.add_argument("-o", "--outdir",
                        type=str,
                        required=True,
                        help="The output directory")
    args = parser.parse_args()

    if args.file:
        pass
    elif args.dir:
        gen_edge_from_dir(args.dir, args.outdir)



    # inputfile = sys.argv[1]
    # rootdir    = sys.argv[2]

    # basename = os.path.basename(inputfile)

    # outdir = os.path.join(rootdir, basename)

    # try:
    #     os.mkdir(outdir, 0o755)
    # except OSError as err:
    #     print(err)

    # php_ext = PHPExtractor()

    # php_xml_dom_obj = php_ext.parse(inputfile)
    # php_xml_dom = php_xml_dom_obj.analyze()

    # name, xml = php_xml_dom[0]
    # main = xml['main']
    # out_edge_list(main['edge_list'], os.path.join(outdir, f"edge.nx"))





if __name__ == "__main__":
    sys.exit(main())













