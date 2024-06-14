import os
import re

from tika import parser as tika_parser
from pdfminer.high_level import extract_text
from pypdf import PdfReader
import spacy

from langchain_community.document_loaders import UnstructuredFileLoader, JSONLoader

# os.environ["TIKA_SERVER_JAR"] = "https://repo1.maven.org/maven2/org/apache/tika/tika-server/1.19/tika-server-1.19.jar"
# os.environ["no_proxy"] = "http://localhost:9998/tika"    

# https://github.com/chrismattmann/tika-python
# https://github.com/pdfminer/pdfminer.six

CACHE_DIR = "/space/hotel/phit/personal/applied-data-science/cache"

os.environ["no_proxy"] = "localhost"

class Parser:
    
    def __init__(self, path, _type):
        self.path = path
        
    def __str__(self):
        return f"FieldParser({self.path}, {self.type})"
    
    @staticmethod
    def extract_contact_number_from_resume(text):
        contact_number = None

        # Use regex pattern to find a potential contact number
        pattern = r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
        match = re.search(pattern, text)
        if match:
            contact_number = match.group()

        return contact_number
    
    @staticmethod
    def extract_email_from_resume(text):
        email = None

        # Use regex pattern to find a potential email address
        pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        match = re.search(pattern, text)
        if match:
            email = match.group()
        return email
    
    @staticmethod
    def extract_name(doc):
        # Use spacy to extract the name from the text
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text
        return None

    @staticmethod
    def extract_job_type(doc):
        # Use spacy to extract the job type from the text
        for token in doc:
            if token.text.lower() in ["job", "position", "role"]:
                job_type = []
                for child in token.children:
                    if child.pos_ == "NOUN":
                        job_type.append(child.text)
                return " ".join(job_type)
        return None

    @staticmethod
    def extract_experience(doc):
        # Use spacy to extract the experience from the text
        for sent in doc.sents:
            if "experience" in sent.text.lower():
                experience = []
                for token in sent:
                    if token.pos_ == "NUM":
                        experience.append(token.text)
                return " ".join(experience)
        return None
    
    @staticmethod
    def extract_education(doc):
        # Use spacy to extract the education from the text
        for sent in doc.sents:
            if "education" in sent.text.lower():
                education = []
                for token in sent:
                    if token.pos_ == "NOUN":
                        education.append(token.text)
                return " ".join(education)
        return None
    
    @staticmethod
    def extract_skills_from_resume(text, skills_list):
        skills = []

        for skill in skills_list:
            pattern = r"\b{}\b".format(re.escape(skill))
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                skills.append(skill)

        return skills
    
    @staticmethod
    def parse(text, use_llm=False):
        if use_llm:
            from transformers import AutoTokenizer, AutoModelForCausalLM

            tokenizer = AutoTokenizer.from_pretrained("google/gemma-7b", cache_dir=CACHE_DIR)
            model = AutoModelForCausalLM.from_pretrained("google/gemma-7b", device_map="auto", cache_dir=CACHE_DIR)

            input_text = f"Perform named entity recognition on the following text: {text}"
            input_ids = tokenizer(input_text, return_tensors="pt").to("cuda")

            outputs = model.generate(**input_ids, max_new_tokens=240)
            print(tokenizer.decode(outputs[0]))
        else:
            # Use spacy to extract all the information from the text
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(text)
            name = None
            job_type = None
            experience = None
            education = None
            skills = None
            if name is None:
                name = Parser.extract_name(doc)
            if job_type is None:
                job_type = Parser.extract_job_type(doc)
            if experience is None:
                experience = Parser.extract_experience(doc)
            if education is None:
                education = Parser.extract_education(doc)
            if skills is None:
                skills = Parser.extract_skills(doc)
            return {
                "name": name,
                "job_type": job_type,
                "experience": experience,
                "education": education,
                "skills": skills
            }

    
    
class PDFParser(Parser):
    def __init__(self, path, _type):
        super().__init__(path, _type)
        self.type = _type
        if self.type not in ["tika", "pdfminer", "pypdf"]:
            raise ValueError("Invalid type")
    
    def get_text(self):
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
 
    
class ImageParser(Parser): #TODO: Implement OCR model here
    def __init__(self, path, _type):
        super().__init__(path, _type)
        self.type = _type
        if self.type not in ["tesseract"]:
            raise ValueError("Invalid type")
    
    def get_text(self):
        if self.type == "tesseract":
            pass
    
    def __str__(self):
        return f"ImageParser({self.path}, {self.type})"


def get_parser(path, _type):
    extension = os.path.splitext(path)[1]
    if extension == ".pdf":
        return PDFParser(path, _type)
    elif extension in [".jpg", ".jpeg", ".png"]:
        return ImageParser(path, _type)
    else:
        raise ValueError("Invalid file extension")



# if __name__ == "__main__":
#     _type = "pypdf"
#     parser = get_parser("data/cv/Bui Tien Phat resume (1).pdf", _type)
#     res = parser.get_text()
#     with open(f"result_{_type}.txt", "w") as f:
#         f.write(res)
#     # print(res)
#     parser.parse(res, use_llm=True)
