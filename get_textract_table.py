import pandas as pd
import boto3
import os

TABLE_OUTPUT_FOLDER = "output_tables"

def get_rows_columns_map(table_result, blocks_map):
    rows = {}
    for relationship in table_result['Relationships']:
        if relationship['Type'] == 'CHILD':
            for child_id in relationship['Ids']:
                cell = blocks_map[child_id]
                if cell['BlockType'] == 'CELL':
                    row_index = cell['RowIndex']
                    col_index = cell['ColumnIndex']
                    if row_index not in rows:
                        rows[row_index] = {}
                    rows[row_index][col_index] = get_text(cell, blocks_map)
    return rows

def get_text(result, blocks_map):
    text = ''
    if 'Relationships' in result:
        for relationship in result['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    word = blocks_map[child_id]
                    if word['BlockType'] == 'WORD':
                        text += word['Text'] + ' '
    return text.strip()


def get_table_data(file_name):
    doc_id = file_name.rsplit("/", 1)[-1].rsplit(".", 1)[0]

    if not os.path.exists(f"{TABLE_OUTPUT_FOLDER}/{doc_id}"):
        os.makedirs(f"{TABLE_OUTPUT_FOLDER}/{doc_id}")
    else:
        print(f"Tables already exists: {TABLE_OUTPUT_FOLDER}/{doc_id}")
        table_data = get_all_tables_in_folder(f"{TABLE_OUTPUT_FOLDER}/{doc_id}")
        return table_data


    with open(file_name, 'rb') as file:
        img_test = file.read()
        bytes_test = bytearray(img_test)
        print('Image loaded', file_name)

    
    # process using image bytes
    session = boto3.Session()
    client = session.client('textract')
    response = client.analyze_document(Document={'Bytes': bytes_test}, FeatureTypes=['TABLES'])

    # Get the text blocks
    blocks = response['Blocks']

    blocks_map = {}
    table_blocks = []
    for block in blocks:
        blocks_map[block['Id']] = block
        if block['BlockType'] == "TABLE":
            table_blocks.append(block)

    if len(table_blocks) == 0:
        return "<b>NO Table FOUND</b>"

    table_data = []
    for index, table in enumerate(table_blocks):
        rows = get_rows_columns_map(table, blocks_map)
        df = pd.DataFrame.from_dict(rows, orient='index')
        table_data.append(df)

        df.to_csv(f"{TABLE_OUTPUT_FOLDER}/{doc_id}/Table_{index}.CSV", index=False)

    return table_data


def get_textract_table(file_name):
    table_data = get_table_data(file_name)
    return table_data


def get_all_tables_in_folder(folder_path):
    table_data = []
    for root, _, filenames in os.walk(folder_path):
        for filename in filenames:
            if filename.rsplit(".", 1)[-1].lower() == 'csv':
                table_data.append(pd.read_csv(os.path.join(root, filename)))
    return table_data


if __name__ == "__main__":
    all_tables = get_table_data("/Users/salman/workspace/glimpse/assignment/dataset/images/train_grayscale/Stationery-Purchase-Order-Template-TemplateLab.com_.pdfpage_1.PNG")
