#! /usr/bin/env nix-shell
#! nix-shell -i python3 -p "python3.withPackages(ps: [ps.pypdf2 ps.pymupdf])"

import argparse
import fitz
import time
from PyPDF2 import PdfFileReader

def main():
    parser = argparse.ArgumentParser(description='make movies from beamer slides')
    parser.add_argument('input', default='texput.pdf', nargs='?')
    parser.add_argument('output', default='input.xml', nargs='?')

    args = parser.parse_args()

    doc = fitz.open(args.input)

    output = open(args.output, 'w')
    output.write('<?xml version="1.0" encoding="UTF-8"?>' + "\n")
    output.write('<movie>' + "\n")

    with open(args.input, 'rb') as f:
        pdf = PdfFileReader(f)
        info = pdf.getDocumentInfo()
        number_of_pages = pdf.getNumPages()
        print("Reading through {} pages...".format(number_of_pages))
        
        for i in range(number_of_pages):
            print("Page {}".format(i))
            
            page = pdf.getPage(i)
            
            fitzpage = doc[i]
            mat = fitz.Matrix(4,4)
            pix = fitzpage.getPixmap(matrix = mat, alpha=True)
            zoom = 4.0 * float(1080) / pix.height

            mat = fitz.Matrix(zoom,zoom)
            pix = fitzpage.getPixmap(matrix = mat, alpha=True)

            png = 'page{:03d}.png'.format(i)
            pix.writePNG(png)

            kind = 'wait'
            contents = '5'

            count = 0
            for annot in page['/Annots']:
                # Other subtypes, such as /Link, cause errors
                subtype = annot.getObject()['/Subtype']
                if subtype == "/Text":
                    if annot.getObject()['/T'] == 'Wait':
                        kind = 'wait'
                        contents = annot.getObject()['/Contents']
                    if annot.getObject()['/T'] == 'Audio':
                        kind = 'audio'
                        contents = annot.getObject()['/Contents']
                    if annot.getObject()['/T'] == 'Video':
                        kind = 'video'
                        contents = annot.getObject()['/Contents']
                    count = count + 1
                    if count > 1:
                        raise Exception("Too many annotations on page " + str(i+1))
            if kind == 'audio':
                output.write('  <video src="{}" slide="{}" />'.format(contents, png) + "\n")
            elif kind == 'video':
                output.write('  <video src="{}" />'.format(contents) + "\n")
            elif kind == 'wait':
                output.write('  <video src="{}" in="0" out="{}"/>'.format(png,contents) + "\n")

            
        output.write('</movie>' + "\n")                    
        output.close()
        print("Wrote " + args.output)
        
main()
