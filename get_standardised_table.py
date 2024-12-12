import re
import pandas as pd
from get_textract_table import get_textract_table

HEADER_MAPPING_DATA = {"itemdescription": "Product_Name", 
                       "items": "Product_Name",
                       "productname": "Product_Name",
                       "description": "Product_Name",
                       "item": "Product_Name",
                       "details": "Product_Name",
                       "vehicleand accessories": "Product_Name",
                       "varietal": "Product_Name",
                       "productdescription": "Product_Name",
                       "vehicleandaccessories":"Product_Name",
                       "iditemdescription":"Product_Name"}

# Can be done using configs or ML
TABLE_END_WORDS = ['Total', 'receipt of the items']
IRRELEVANT_WORDS = ["Description", "receipt"]
FIXED_COLUMNS = ['Supplier']

THRESHOLD = 60
HEADER_WORDS = ['description',
                'productname',
                'accessories',
                'quantities',
                'unitprice', 
                'linetotal',
                'priceinfo',
                'supplier',
                'discount',
                'quantity', 
                'vintage', 
                'vehicle',
                'varietal',
                'colour',
                'amount',
                'total', 
                'color', 
                'item',
                'unit',
                'code', 
                'qty',
                ]

def get_clean_word_list(word_list):
    """
    makes a list of words split on punctuations, only characters are left in words
    """
    lines = [re.split("\s|\.|-|/|\\||_", word.lower()) for word in word_list if word]
    cleaned_words_list = []
    lines = [j for sub in lines for j in sub]  # flatten the list
    for word in lines:
        cleaned_words_list.append(''.join(e for e in word if e.isalnum()))
    return cleaned_words_list


def get_bow_percentage(cleaned_words_list, header_bag_of_words=HEADER_WORDS):
    """
    returns percentage match_score of row_words(list)
    with header bow
    """
    line_string = ''.join(cleaned_words_list)
    line_string_length = len(line_string)
    if line_string_length == 0:
        return 0
    match = 0
    i = 0
    while i < len(header_bag_of_words):
        initial = len(line_string)
        word = header_bag_of_words[i]
        if word in line_string:
            line_string = line_string.replace(word, "")
            final = len(line_string)
            match = match + (initial - final)
        else:
            i = i + 1
    match_score = 100 * match / line_string_length
    return match_score


def get_relevant_table(image_path):
    tables = get_textract_table(image_path)

    relevant_table = pd.DataFrame()
    for table in tables:
        table = table.fillna("").astype(str)
        word_list = get_clean_word_list(list(table.iloc[0]))
        match_score = get_bow_percentage(word_list, HEADER_WORDS)
        print(word_list, match_score )
        if match_score>THRESHOLD and len(table.columns)>1:
            print("Relevant_Table_Detected!")
            relevant_table = table.copy()
            relevant_table.columns = [HEADER_MAPPING_DATA.get(col.lower().replace(" ", ""), col) for col in table.iloc[0]]
            relevant_table = relevant_table.iloc[1:].reset_index(drop=True)
            break
    if len(relevant_table)>0:
        relevant_table = apply_fixed_column_filter(relevant_table)
        relevant_table = remove_irrelevant_lines(relevant_table)
        return get_products_from_table(relevant_table)
    return []


def remove_irrelevant_lines(table):
    """
    Identify relevant lines using some words or config(deterministic)
    Mark irrelevant rows as 0
    """
    if len(table)>0 and "Product_Name" in table.columns:
        table['Irrelevent_Rows'] = 1
        for idx, row_value in enumerate(table['Product_Name']):
            if any([value for value in IRRELEVANT_WORDS if value.lower() == row_value.lower()]):
                table.loc[idx, 'Irrelevent_Rows'] = 0

        end_table_idx = -1
        for idx, row_value in enumerate(table['Product_Name']):
            if any([value for value in TABLE_END_WORDS if value.lower() in row_value.lower()]):
                end_table_idx = idx
                break
        if end_table_idx!=-1:
            table.loc[end_table_idx:, 'Irrelevent_Rows'] = 0
        return table[table['Irrelevent_Rows']==1]
    return table


def apply_fixed_column_filter(table):
    for col in table.columns:
        if col in FIXED_COLUMNS:
            print("Inside")
            table = table[table[col]!='']
    return table
    

def process_words(word_list):
    result = []
    for i in range(len(word_list)):
        if word_list[i] != "":
            result.append(word_list[i])
        elif i > 0 and word_list[i] == "" and word_list[i-1] == "":
            break
    return result


def get_products_from_table(table):
    if "Product_Name" in table.columns:
        return [product for product in process_words(table["Product_Name"].tolist()) if product] 
    return []

if __name__ == "__main__":
    image_path = "/Users/salman/workspace/glimpse/assignment/dataset/images/train_grayscale/Graphic-Design-Purchase-Order-Template-TemplateLab.com_.pdfpage_1.PNG"
    output = get_relevant_table(image_path)
    print(output)