import base64
import numpy as np
import pytesseract
from django.contrib import messages
from django.shortcuts import render
from PIL import Image
import json
from fpdf import FPDF
#install tesseract module too from here - https://github.com/UB-Mannheim/tesseract/wiki
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Path to tesseract.exe
)

def convert(f):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial",size=15)
    for x in f:
        pdf.multi_cell(200, 8, txt = x, align = 'L')
    k = pdf.output("Test1.pdf")  
    return k

def homepage(request):
    if request.method == "POST":
        try:
            image = request.FILES["imagefile"]
            # encode image to base64 string
            image_base64 = base64.b64encode(image.read()).decode("utf-8")
                        

        except:
            messages.add_message(
                request, messages.ERROR, "No image selected or uploaded"
            )
            return render(request, "home.html")

        print(type(image))
        lang = request.POST["language"]
        
        img = np.array(Image.open(image))

        text = pytesseract.image_to_string(img, lang=lang)
           


        text_list = text.split("\n")


    
        # return text to html
        return render(request, "home.html", {"ocr": text, "image": image_base64, "text_length" : len(text_list)})

    return render(request, "home.html")