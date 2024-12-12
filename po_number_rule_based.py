import re
from get_ocr import extract_words_from_pdf
KEYWORDS = ["po", "ponumber","purchaseorder"]

PO_REGEX_PATTERN = "\\d{4,9}[-\/]\d{2,4}|[A-Za-z]+-?\\d{5,7}|\\d{5,10}"


def extract_po_number(image_path):
    wdf = extract_words_from_pdf(image_path)
    po_number = []
    
    for idx, row in wdf.iterrows():
        if any(word in re.sub(r'[^A-Za-z]', '', row['word'].lower())  for word in KEYWORDS):
            reference_box = [row["x0"], row["top"], row["x1"], row["bottom"]]  # Bounding box of the keyword
            x0_ref, y0_ref, x1_ref, y1_ref = reference_box

            # Initialize variables for closest right and below words
            closest_right = None
            closest_below = None
            min_right_distance = float('inf')
            min_below_distance = float('inf')
            minx = min(idx, idx-2)

            for _, candidate in wdf.loc[minx:].iterrows():
                if candidate['word'].lower() == row['word'].lower():  # Skip the keyword itself
                    continue
        
                candidate_text = candidate['word']
                x0, y0, x1, y1 = [candidate["x0"], candidate["top"], candidate["x1"], candidate["bottom"]]

                # Check if candidate is immediately to the right
                if x0 > x1_ref and not (y1 < y0_ref or y0 > y1_ref):  # Horizontally aligned
                    distance = x0 - x1_ref
                    if distance < min_right_distance:
                        min_right_distance = distance
                        closest_right = candidate_text
                    print(min_right_distance)

                # Check if candidate is immediately below
                if  y0 > y1_ref and x1 > x0_ref and x0 < x1_ref:  # Vertically aligned
                    distance = y0 - y1_ref
                    if distance < min_below_distance:
                        min_below_distance = distance
                        closest_below = candidate_text

            input_string = f"{row['word']} {closest_right} {closest_below}"
            po_number = re.findall(PO_REGEX_PATTERN, input_string)
            if po_number:
                break

    return po_number



if __name__ == "__main__":
    # filename = "/Users/salman/workspace/glimpse/assignment/dataset/images/train_grayscale/Electronic-Purchase-Order-Template-TemplateLab.com_.PNG"
    # po_number = extract_po_number(filename)
    # print("Extracted PO Number:", po_number)
    import os
    import pandas as pd
    from tqdm import tqdm

    folder_path = "dataset/images/train_grayscale"
    pos, files = [], []
    for file in ["Purchase-Order-Template-02-TemplateLab.com_.PNG"]:
    # tqdm(os.listdir(folder_path)):
    # ['Wholesale-Purchase-Order-Template-TemplateLab.com_.PNG']:

        if file.endswith("PNG"):
            print(file)
            img_path = os.path.join(folder_path, file)
            po = extract_po_number(img_path)
            pos.append(po)
            files.append(file)
    pd.DataFrame({"pos":pos, "file":files}).to_csv("po.csv", index=False)
    print(pd.DataFrame({"pos":pos, "file":files}))
    print(os.listdir(folder_path))