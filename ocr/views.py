import base64
import numpy as np
import pytesseract
from pytesseract import Output
from django.contrib import messages
from django.shortcuts import render
from PIL import Image
import json
import os 
import cv2
from fpdf import FPDF
from pdf2image import convert_from_path, convert_from_bytes
#install tesseract module too from here - https://github.com/UB-Mannheim/tesseract/wiki
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Path to tesseract.exe
)

final_text = []
# get grayscale image
def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# noise removal
def remove_noise(image):
    return cv2.medianBlur(image,5)
 
#thresholding
def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

def dilate(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.dilate(image, kernel, iterations = 1)
    
#erosion
def erode(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.erode(image, kernel, iterations = 1)

#opening - erosion followed by dilation
def opening(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

#canny edge detection
def canny(image):
    return cv2.Canny(image, 100, 200)

#skew correction
def deskew(image):
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

#template matching
def match_template(image, template):
    return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED) 

def extract_text(image_path):

    img = cv2.imread(image_path)
    img = get_grayscale(img)
    # img = remove_noise(img)
    img = thresholding(img)

    return img

def mark_region(image_path):
    
    img = cv2.imread(image_path)
    # img = get_grayscale(img)
    # # img = remove_noise(img)
    # img = thresholding(img)

    d = pytesseract.image_to_data(img, output_type=Output.DICT)
    print(d.keys())

    n_boxes = len(d['text'])
    
    for i in range(n_boxes):
        if float(d['conf'][i]) > int(60):
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    return img

def homepage(request):
    if request.method == "POST":
        try:
            image = request.FILES["imagefile"]
            # image_base64 = base64.b64encode(image.read()).decode("utf-8")
            pages = convert_from_bytes(image.read())
            text_file = image
            
            i = 1

            for page in pages:

                image_name = "Page_" + str(i) + ".jpg"
                page.save(image_name, "JPEG")
                base64_path = os.path.abspath(image_name)
                print(base64_path)
                i = i+1

                image = mark_region(os.path.abspath(image_name))
                text_file = extract_text(os.path.abspath(image_name))
                
                final_text.append(pytesseract.image_to_string(text_file).split("\n"))
                
                image_base64 = cv2.imwrite(image_name, image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])

                

                # f = open(image_name, "r")
                # image_base64 = f.read()
                # print(image_base64)
                   

        except:
            messages.add_message(
                request, messages.ERROR, "No image selected or uploaded"
            )
            return render(request, "home.html")

        # print(type(image))
        lang = request.POST["language"]
        

        text = pytesseract.image_to_string(text_file, lang=lang)
           


        text_list = text.split("\n")

        print(final_text)
    
        # return text to html
        return render(request, "home.html", {"ocr": text, "image": image_base64, "text_length" : len(text_list)})

    return render(request, "home.html")