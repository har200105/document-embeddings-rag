from enum import Enum
from rest_framework.response import Response
from docx import Document as DocxDocument
import PyPDF2

class Errors(Enum):
    SOMETHING_WENT_WRONG = 1
    OBJECT_NOT_FOUND = 2
   


error_map = {
    Errors.SOMETHING_WENT_WRONG : 'Something went wrong',
}


def prepare_failure_response(code, msg='',statusCode=200):
    if msg == '':
        msg = error_map.get(code)
    return Response({"success": False, "code": code.name, "errorMsg": msg},status=statusCode)


def prepare_success_response(data, msg=''):
    return Response({"success": True, "msg": msg, "data": data})



def extract_text_from_file(file) -> str:
    filename = file.name.lower()

    try:
        if filename.endswith('.pdf'):
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
            return text.strip()

        elif filename.endswith('.docx'):
            doc = DocxDocument(file)
            return '\n'.join([para.text for para in doc.paragraphs]).strip()

        elif filename.endswith('.txt'):
            return file.read().decode('utf-8').strip()

        else:
            raise ValueError("Unsupported file type (.doc is not supported without system packages)")

    except Exception as e:
        raise ValueError(f"Failed to extract text: {str(e)}")
