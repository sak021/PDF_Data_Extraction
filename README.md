Data Extraction From Documents
Streamlit App

1. Create Virtual Environment
2. Install Required Libraries enlisted in requirements.txt --> pip install -r requirements.txt
3. Get .env file and place it in task folder
4. Run app.py--> streamlit run app.py


Folder Structure and File Description   
PDF_DATA_Extraction  
|--- app.py:  Main file to run the app  
|--- get_ocr.py:  To get the OCR  
|--- po_number_rule_based.py Get PO number rule based  
|--- get_textract_table.py: Get data from AWS Textract  
|--- get_standardised_table.py: Get Standardised Table from Textract 
