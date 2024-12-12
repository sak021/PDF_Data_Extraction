import os
# import pytesseract
import pandas as pd
from PIL import Image
from paddleocr import PaddleOCR

OCR_DATA_PATH = os.path.join(os.getcwd(), "ocr_data")

# PYTESSERACT OCR CODE
# def extract_words1_from_pdf(image_path, page_num=0):
#     """
#     PyTesseract
#     """
#     filename = image_path.rsplit("/",1)[-1].rsplit(".",1)[0]
#     parque_filename = f"{OCR_DATA_PATH}/{filename}.parquet"
#     if os.path.exists(parque_filename):
#         print("OCR Data Exists")
#         word_df = pd.read_parquet(parque_filename, engine='pyarrow')
#         return word_df

#     # images = convert_from_path(f"{PDF_DATA_PATH}/{filename}")
#     image = Image.open(image_path)
#     word_data = []
#     global_line_num = 0
#     # for page_num, image in enumerate(images):
#     image_width, image_height = image.size
#     data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    
#     for i in range(len(data['text'])):
#         if i > 0 and data['line_num'][i] == 1:
#             global_line_num += 1

#         word_data.append({
#             "page_num": page_num + 1,
#             "word": data['text'][i],
#             "x0": data['left'][i]/image_width,
#             "top": data['top'][i]/image_height,
#             "x1": (data['left'][i] + data['width'][i])/image_width,
#             "bottom": (data['top'][i] + data['height'][i])/image_height,
#             "line_id": global_line_num
#         })

#     word_df = pd.DataFrame(word_data)
#     word_df.to_parquet(parque_filename, engine='pyarrow')
#     return word_df




def extract_words_from_pdf(image_path, page_num=0):
    """
    Paddle OCR
    """
    filename = image_path.rsplit("/", 1)[-1].rsplit(".", 1)[0]

    parque_filename = f"{OCR_DATA_PATH}/{filename}_.parquet"
    if os.path.exists(parque_filename):
        print("OCR Data Exists")
        word_df = pd.read_parquet(parque_filename, engine='pyarrow')
        return word_df

    # Load the image (Assuming it's a single page PDF converted to image)
    image = Image.open(image_path)

    # Initialize PaddleOCR
    ocr = PaddleOCR(use_angle_cls=True, lang='en')  # You can adjust the language here

    # Perform OCR on the image
    result = ocr.ocr(image_path, cls=True)

    word_data = []
    global_line_num = 0

    # Iterate through the results
    for line in result[0]:
        word_text = line[1][0]
        # Extracting bounding box coordinates
        x0, y0, x1, y1 = line[0][0][0], line[0][0][1], line[0][2][0], line[0][2][1]

        # Normalize the coordinates with respect to image size
        image_width, image_height = image.size
        word_data.append({
            "page_num": page_num + 1,
            "word": word_text,
            "x0": x0 / image_width,
            "top": y0 / image_height,
            "x1": x1 / image_width,
            "bottom": y1 / image_height,
            "line_id": global_line_num
        })
        # Increment line number (if needed, adjust based on your OCR result format)
        global_line_num += 1

    word_df = pd.DataFrame(word_data)
    word_df.to_parquet(parque_filename, engine='pyarrow')
    return word_df



if __name__ == "__main__":
    folder_path = ""
    filename = "Construction-Purchase-Order-Template-TemplateLab.com_.pdf"
    wdf = extract_words_from_pdf(filename)

    # Show first few rows of word_df
    print(wdf.head())
