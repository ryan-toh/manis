import re
import pandas as pd
from typing import List, Optional, Tuple
from common import Detection

#Main function to detect regex and check if filter is needed
#Input: dataframe df, optional list[str] columns
def detect_regex(df, columns = None):

    detections_list = []

    #If columns is empty, take all columns
    if columns is None:
        # columns = df.select_dtypes().columns.tolist()
        columns = df.columns.tolist()

    #Iterate through each column/row and add detection object to detection_list if found
    for col in columns:
        for rowid, text in df[col].items():
            apply_regex(detections_list, text, col, rowid)

    #Output: List of Detection objects
    return detections_list

#Apply all the regex methods onto the column and appends the detection object to the back of the list
def apply_regex(detection_list,text, col, rowid):
    text = str(text)  # Ensure text is a string
    find_emails(detection_list, text, col, rowid)
    find_phones(detection_list, text, col, rowid)
    find_credit_cards(detection_list, text, col, rowid)
    find_ips(detection_list, text, col, rowid)


def find_emails(detection_list, text, col, rowid):
    #Regex pattern for emails
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    matches = re.finditer(email_pattern, text)
    #Create a detection object for each match and append it to the back of the list
    for match in matches:
        new_detection = Detection(
            row = rowid,
            col = col,
            start = match.start(),
            end = match.end(),
            label = "EMAIL",
            value = match.group()
        )
        detection_list.append(new_detection)


def find_phones(detection_list, text, col, rowid):
    # Implement phone detection regex
    phone_pattern = r"\+?[1-9]\d{1,14}"
    matches = re.finditer(phone_pattern, text)
    for match in matches:
        new_detection = Detection(
            row = rowid,
            col = col,
            start = match.start(),
            end = match.end(),
            label = "PHONE",
            value = match.group()
        )
        detection_list.append(new_detection)

def find_credit_cards(detection_list, text, col, rowid):
    # Implement credit card detection regex
    credit_card_pattern = r"\b(?:\d[ -]*?){13,16}\b"
    matches = re.finditer(credit_card_pattern, text)
    for match in matches:
        new_detection = Detection(
            row = rowid,
            col = col,
            start = match.start(),
            end = match.end(),
            label = "CREDIT_CARD",
            value = match.group()
        )
        detection_list.append(new_detection)

def find_ips(detection_list, text, col, rowid):
    # Implement IP detection regex
    ip_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    matches = re.finditer(ip_pattern, text)
    for match in matches:
        new_detection = Detection(
            row = rowid,
            col = col,
            start = match.start(),
            end = match.end(),
            label = "IP",
            value = match.group()
        )
        detection_list.append(new_detection)

#Goal: detect emails, phones, credit cards, IPs using regex.
#Files: src/detect/my_regex.py, tests with a few fake examples.
#Return positions or matched strings for redaction

# from typing import List, Optional
# import pandas as pd
# from .types import Detection  # or import Detection from a shared place

# def detect_regex(
#     df: pd.DataFrame,
#     columns: Optional[List[str]] = None
# ) -> List[Detection]:
#     """
#     Run built-in regexes for EMAIL, PHONE, CREDIT_CARD, IP on the chosen columns.
#     Input:  df
#             columns -> list of columns to scan; if None, scan all df columns that are strings
#     Output: list of Detection objects
#     """

# # (Optional helpers you might expose, but not required by the CLI)
# def find_emails(text: str) -> List[Tuple[int, int, str]]: ...
# def find_phones(text: str) -> List[Tuple[int, int, str]]: ...
# def find_credit_cards(text: str) -> List[Tuple[int, int, str]]: ...
# def find_ips(text: str) -> List[Tuple[int, int, str]]: ...
# # Each returns a list of (start, end, value) for a single string.
