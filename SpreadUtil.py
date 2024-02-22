import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import time
import json
from string import ascii_uppercase

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = json.load(open("Spreadsheetid.json"))["id"]

credentials = None

if os.path.exists("token.json"):
    credentials = Credentials.from_authorized_user_file("token.json", SCOPES)
if not credentials or not credentials.valid:
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        credentials = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(credentials.to_json())

service = build("sheets", "v4", credentials=credentials)
sheets = service.spreadsheets()


def flatten(lst):
    """flattens a two dimensions list"""
    flat = []
    for i in lst:
        if not i:
            flat.append("")
        else:
            for j in i:
                flat.append(j)
    return flat


def column_list_from_cell(sheet, column, firstrow):  # str, str, int, int
    """Returns a list of data in a column from the given cell to the last cell with data (include blanks)"""
    lst = sheets.values().get(spreadsheetId=SPREADSHEET_ID,
                              range=sheet + "!" + column + firstrow + ":" + column).execute()
    try:
        return flatten(lst["values"])
    except:
        pass


def full_column_list(sheet, column):  # Str, Str, Str
    """Returns a list of data in a column from row 1 to the last cell with data (include blanks till last value)"""
    lst = sheets.values().get(spreadsheetId=SPREADSHEET_ID,
                              range=sheet + "!" + column + "1" + ":" + column,).execute()
    try:
        return flatten(lst["values"])
    except:
        pass


def row_list_from_cell(sheet, row, firtcolumn):  # row_list_from_cell("Hoja 2", "1", "B")
    """Returns a list of values on a row from the given cell to the last cell with data (Includes blanks)"""
    lst = sheets.values().get(spreadsheetId=SPREADSHEET_ID,
                              range=sheet + "!" + firtcolumn + row + ":" + row, ).execute()
    try:
        return flatten(lst["values"])
    except:
        pass


def full_row_list(sheet, row):  # Str, Str
    """Returns a list o data in a row from A to Z (include blanks till last value)"""
    lst = sheets.values().get(spreadsheetId=SPREADSHEET_ID,
                                 range=sheet + "!" + "A" + row + ":" + "Z" + row).execute()
    try:
        return flatten(lst["values"])
    except:
        pass


def write_value(sheet, value, col, row):  # str, str, str, str
    """Writes a value on the given coordinates"""
    sheets.values().update(spreadsheetId=SPREADSHEET_ID, range=sheet + "!" + col + row,
                           valueInputOption="USER_ENTERED",  body={"values": [[value]]}).execute()


def find_column(sheet, row, value):
    """Finds the column where the given value is in the given row (from A to Z)"""
    dict = {}
    for i, j in zip(full_row_list(sheet, row), ascii_uppercase):
        dict[i] = j
    return dict[value]


def find_row(sheet, column, value):
    """Finds the row where the given value is in a given column from row 1 to row 1000"""
    dict = {}
    for i, j in zip(full_column_list(sheet, column), range(1, 1000)):
        dict[i] = j
    return dict[value]


def find_value(sheet, value):
    """Finds a value and returns the coordinates, from A1 to Z1000"""
    coordinates = []
    for i in ascii_uppercase:
        lst = full_column_list(sheet, i)
        if not lst:
            pass
        else:
            if value in lst:
                row = str(lst.index(value) + 1)
                coordinates.append(i + "," + row)
    return coordinates


def find_value_in_column(sheet, column, value):
    """Finds a value in a given column"""
    lst = full_column_list(sheet, column)
    coordinates = []
    counter = 1
    for i in lst:
        if i == value:
            coordinates.append(column + "," + str(counter))
        counter += 1
    return coordinates


def find_value_in_row(sheet, row, value):
    """Finds a value in a given row"""
    lst = full_row_list(sheet, row)
    coordinates = []
    counter = 1
    for i, j in zip(lst, ascii_uppercase):
        if i == value:
            coordinates.append(j + "," + row)
    return coordinates


def find_date(sheet, row):  # Str, Str
    """Finds and returns the column where the current date is in a given row"""
    time_string = time.strftime("%d/%m", time.localtime())
    dic = {}
    for i, j in zip(full_row_list(sheet, row), ascii_uppercase):
        dic[i] = j
    return dic[time_string]


