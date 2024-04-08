import os
from tika import parser as tika_parser
from pdfminer.high_level import extract_text
from pypdf import PdfReader

# os.environ["TIKA_SERVER_JAR"] = "https://repo1.maven.org/maven2/org/apache/tika/tika-server/1.19/tika-server-1.19.jar"
# os.environ["no_proxy"] = "http://localhost:9998/tika"    

os.environ["no_proxy"] = "localhost"

class Parser:
    def __init__(self, path, _type):
        self.path = path
    
class PDFParser(Parser):
    def __init__(self, path, _type):
        super().__init__(path, _type)
        self.type = _type
        if self.type not in ["tika", "pdfminer", "pypdf"]:
            raise ValueError("Invalid type")
    
    def parse(self):
        if self.type == "tika":
            raw = tika_parser.from_file(self.path)
            return raw["content"]
        elif self.type == "pdfminer":
            return extract_text(self.path)
        elif self.type == "pypdf":
            reader = PdfReader(self.path)
            number_of_pages = len(reader.pages)
            page = reader.pages[0]
            text = page.extract_text()
            return text
        
    def __str__(self):
        return f"PDFParser({self.path}, {self.type})"

if __name__ == "__main__":
    _type = "pypdf"
    parser = PDFParser("../cv/CV _ Đinh Tuấn Nam_BE Developer(.NET)_HCM.pdf", _type)
    res = parser.parse()
    with open(f"result_{_type}.txt", "w") as f:
        f.write(res)
    print(res)