import os
import cv2
import numpy as np
from pdf2image import convert_from_path
from PIL import Image
from get_standardised_table import get_relevant_table
from po_number_rule_based import extract_po_number
from dotenv import load_dotenv
load_dotenv()

GRAYSCALE_IMG_FOLDER = "dataset/images/train_grayscale"

def lambda_handler(pdf_path):
    filename = pdf_path.rsplit("/",1)[-1].rsplit(".",1)[0]
    ext = pdf_path.rsplit(".",1)[-1].lower()
    if ext=="pdf":
        images = convert_from_path(pdf_path, dpi=300)
    elif ext in ["jpg", "png", "jpeg"]:
        images = [Image.open(pdf_path)]
    else: 
        return [], []

    # Asssuming only 1 pages
    for _, image in enumerate(images):
        image_path = convert_to_greyscale(image, filename)
        po_num = extract_po_number(image_path)
        # get_po_number(image_path)
        products = get_relevant_table(image_path)
    return po_num, products


def convert_to_greyscale(image, filename):
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    output_path = f"{GRAYSCALE_IMG_FOLDER}/{filename}.PNG"
    cv2.imwrite(os.path.join(output_path), gray)
    return output_path


if __name__ == "__main__":

    import streamlit as st
    from pathlib import Path

    # Set Streamlit app title
    st.title("Purchase Order and Product Name Extractor")

    # File uploader for PDF or image
    uploaded_file = st.file_uploader("Upload a PDF or Image", type=["pdf", "jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Save uploaded file to a temporary path
        temp_file_path = Path(f"{uploaded_file.name}")
        temp_file_path.write_bytes(uploaded_file.read())

        st.write("Processing the file...")

        # Call your lambda_handler function
        try:
            po, product = lambda_handler(str(temp_file_path))

            # Display results
            st.write(f"**Purchase Order (PO):** {po}")
            st.write("**Product Name:**")
            st.markdown("\n".join([f"- {item}" for item in product]))
        except Exception as e:
            st.error(f"An error occurred: {e}")

        # Clean up the temporary file
        temp_file_path.unlink()  # Delete the temporary file

    else:
        st.info("Please upload a PDF or Image file to extract information.")


    # import pandas as pd
    # folder_path = "POs"
    # pos, products = [], []
    # for file in ["Electronic-Purchase-Order-Template-TemplateLab.com_.pdf"]:
    # # os.listdir("POs"):
    #     print(file)
    #     pdf_path = os.path.join(folder_path, file)
    #     po, product = lambda_handler(pdf_path)
    #     print(po, product)
