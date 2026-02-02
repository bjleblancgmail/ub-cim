import zipfile
import xml.etree.ElementTree as ET
import sys
import os

def read_docx(filepath):
    """Extract text from a .docx file"""
    text_parts = []

    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        # Read the main document
        with zip_ref.open('word/document.xml') as xml_file:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            # Define namespace
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

            # Find all text elements
            for elem in root.iter():
                if elem.tag.endswith('}t'):
                    if elem.text:
                        text_parts.append(elem.text)
                elif elem.tag.endswith('}p'):
                    text_parts.append('\n')

    return ''.join(text_parts)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        if os.path.exists(filepath):
            print(read_docx(filepath))
        else:
            print(f"File not found: {filepath}")
    else:
        print("Usage: python read_docx.py <filepath>")
