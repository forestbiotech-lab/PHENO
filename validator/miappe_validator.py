# Script to read and validate input MIAPPE Compliant Excel file.

# Read required packages
from pyexcel_ods3 import get_data
import pandas as pd
import json
import sys
from re import search
# Check script execution time
from datetime import datetime

startTime = datetime.now()


#   ---   Define a Miappe_validator Class   ---
class Miappe_validator:
    #   ---   Initiate class properties and check Input File extension  ---
    def __init__(self, input_file):
        self.sheet_df = None
        self.valid_sheets = None
        self.invalid_sheets = None
        self.transposed = False
        self.valid_structure = json.load(open("validationstructure.json"))
        self.logs = ["  --- OntoBrAPI - Input File Validity Report ---  "]
        self.run = True
        # Loads file
        self.input_file = input_file
        try:
            if self.input_file.lower().endswith(('.xlsx', '.xls')):
                self.logs.append("CHECK PASSED - Valid input file extension")
                # microsoft
                self.filetype = "ms"
                self.complete_excel = pd.ExcelFile(input_file)
                self.sheetsList = self.complete_excel.sheet_names
            elif self.input_file.lower().endswith(('.ods')):
                self.logs.append("CHECK PASSED - Valid input file extension")
                # open docs
                self.filetype = "od"
                ods = get_data(input_file)
                ##TODO This is might not be setting empty cells different from NA text
                self.complete_excel = {key: pd.DataFrame(ods[key], columns=ods[key][0]) for key in ods.keys()}
                self.sheetsList = self.complete_excel.keys()
            else:
                self.logs.append("CHECK FAILED - Invalid input file extension")
                self.run = False
        except FileNotFoundError:
            self.logs = ["CHECK FAILED - Invalid input file"]
            self.run = False

    #  -  Check sheet number & sheet names  -
    def check_input_file(self):
        # These are all valid sheet names for a MIAPPE compliant excel file
        valid_sheet_names = list(self.valid_structure.keys())
        # Check the number of input sheet names that are valid or not
        self.valid_sheets = [sheet for sheet in self.sheetsList if sheet in valid_sheet_names]
        if len(self.valid_sheets) < (len(valid_sheet_names[:-1]) - 1) and (
                "Exp. Factor" in self.valid_sheets and "Factor" in self.valid_sheets):  # It's [:1] to ignore Data value, and -1 because Factor/Exp. Factor redundancy
            self.invalid_sheets = [sheet for sheet in self.sheetsList if sheet not in valid_sheet_names]
            self.logs.append(
                "CHECK FAILED - The input file has " + str(len(self.valid_sheets)) +
                " valid input sheets, which is less than the minimum 11 valid sheets required: Investigation, Study, Person, Data file, Biological Material, Sample, Observation Unit, Environment, Factor/Exp. Factor, Observed Variable, Event")
            self.logs.append(
                f"CHECK FAILED - The input file has {len(self.invalid_sheets)} " +
                f"invalid input worksheets. Correct the worksheet &lt;&lt;{'&gt;&gt;, &lt;&lt;'.join(self.invalid_sheets)}&gt;&gt;")

            self.run = False
        else:
            if len(self.sheetsList) >= (len(valid_sheet_names[:-1]) - 1):
                self.logs.append(
                    f"CHECK PASSED - The input file has the minimum required {(len(valid_sheet_names[:-1]) - 1)} valid sheet names.")
            else:
                self.logs.append(
                    "CHECK WARNING - The input file has " + str(len(self.sheetsList)) +
                    " sheets, which is more than the minimum 11 valid sheets required. Additional sheets may be discarded.")

    # Deprecation not really feasible since the usage of difernte worksheet name will cause problems with mapping
    def name_of_similar_sheet(self, sheet_name):
        if sheet_name in self.sheetsList:
            return sheet_name
        else:
            try:
                if " " in sheet_name:
                    sheet: str
                    table = str.maketrans(" ", "_")
                    sheet_name = sheet_name.lower().translate(table)
                    return self.sheetsList[[idx for idx, sheet in enumerate(self.sheetsList) if "_" in sheet and
                                            sheet.lower().translate(table) == sheet_name][0]]
            except ValueError:
                # Defers the error
                return sheet_name

    def load_worksheet(self, sheet_name):
        # Solved by not adding the first row
        if self.filetype == "od":
            self.sheet_df = self.complete_excel[sheet_name].drop(0)
            self.sheet_df = self.sheet_df.reset_index(drop=True)
        else:
            self.sheet_df = pd.read_excel(self.complete_excel, self.name_of_similar_sheet(sheet_name),
                                          keep_default_na=False, na_values=["Na", "NA"])
        # Remove '*' characters, which indicate mandatory columns to fill
        header = [ele.replace('*', '') for ele in list(self.sheet_df)]
        headerMap = {ele: ele.replace('*', '') for ele in list(self.sheet_df)}
        # Removes asterisks from columns of data frame
        self.sheet_df = self.sheet_df.rename(columns=headerMap)
        return header

    # Checks if headers are valid
    def validate_headers(self, header, sheet_name):
        if "valid_header1" in self.valid_structure[sheet_name]:
            if header == self.valid_structure[sheet_name]['valid_header1']:
                self.logs.append(f'CHECK PASSED - The {sheet_name} sheet has a valid header (column name/number).')
                self.validate_data(sheet_name)

            elif "valid_header2" in self.valid_structure[sheet_name]:
                if header == self.valid_structure[sheet_name]['valid_header2'] and sheet_name == "Person":
                    ###### Person specific??????
                    # Delete first column and then first three rows of the person dataframe
                    self.sheet_df.drop(["Definition", "Example", "Format"], axis=0, inplace=True)
                    self.sheet_df.drop("Field", axis=1, inplace=True)
                    if header == self.valid_structure[sheet_name]['valid_header2']:
                        # Is used in Study for vitis exception which will be removed.
                        self.logs.append(
                            f'CHECK PASSED - The {sheet_name} sheet has a valid header (column name/number).')
                        self.validate_data(sheet_name)
                    else:
                        self.logs.append(
                            f"CHECK FAILED - The {sheet_name} sheet has an invalid header (column name/number).")
                        self.run = False
                elif sheet_name == "Investigation":
                    # Checks if sheet is transposed, which is the correct version to prevent filling more than 1 Investigation
                    # Checks that are not none from first column
                    header = [ele.replace('*', '') for ele in self.sheet_df.iloc[:, 0].dropna()]
                    if header == self.valid_structure[sheet_name]['valid_header1']:
                        self.transposed = True
                        self.logs.append(
                            f'CHECK PASSED - The {sheet_name} sheet has a valid header (column name/number).')
                    else:
                        self.logs.append("CHECK FAILED - The Investigation sheet has incorrect names in the Field.")
                        self.run = False
                elif header == self.valid_structure[sheet_name]['valid_header2']:
                    self.logs.append(f'CHECK PASSED - The {sheet_name} sheet has a valid header (column name/number).')
                    self.validate_data(sheet_name)
                else:
                    self.logs.append(
                        f"CHECK FAILED - The {sheet_name} sheet has an invalid header (column name/number).")
                    self.run = False
            else:
                self.logs.append(f"CHECK FAILED - The {sheet_name} sheet has an invalid header (column name/number).")
                self.run = False

    # Checks if mandatory columns are filled
    def validate_data(self, sheet_name):
        if 'can_be_empty' in self.valid_structure[sheet_name]:
            if not self.valid_structure[sheet_name]['can_be_empty']:
                if len(self.sheet_df.index) >= 0 and "mandatory_columns" in self.valid_structure[sheet_name]:
                    if (self.transposed == True and sheet_name == "Investigation"):
                        if pd.isna(self.sheet_df.iloc[1, 1]) == True:
                            self.logs.append("CHECK FAILED - The Investigation ID* (Investigation sheet) is required.")
                            self.run = False
                        if pd.isna(self.sheet_df.iloc[2, 1]) == True:
                            self.logs.append(
                                "CHECK FAILED - The Investigation Title* (Investigation sheet) is required.")
                            self.run = False
                        if pd.isna(self.sheet_df.iloc[3, 1]) == True:
                            self.logs.append(
                                "CHECK FAILED - The Investigation Description* (Investigation sheet) is required.")
                            self.run = False
                        if pd.isna(self.sheet_df.iloc[7, 1]) == True:
                            self.logs.append("CHECK FAILED - The MIAPPE Version* (Investigation sheet) is required.")
                            self.run = False
                    else:
                        for idx, row in self.sheet_df.iterrows():
                            mandatory_columns = self.valid_structure[sheet_name]["mandatory_columns"]
                            # Check if any the values in the mandatory columns is empty and ensure they are not all
                            if ((row[mandatory_columns].eq("").any()) and
                                    (not row[mandatory_columns].isna().all())):
                                mandatory_column = []
                                if row[mandatory_columns].eq("").any():
                                    mandatory_column += list(
                                        row[mandatory_columns][row[mandatory_columns].eq("")].index)
                                if row[mandatory_columns].isna().any():
                                    mandatory_column += list(
                                        row[mandatory_columns][row[mandatory_columns].isna()].index)
                                self.logs.append(
                                    f"CHECK FAILED - The *{'* *'.join(mandatory_column)}* column ({sheet_name} sheet) is mandatory in line {idx + 1}.")
                                self.run = False
                else:
                    self.logs.append(f"CHECK FAILED - The {sheet_name} Sheet is empty.")
                    self.run = False

    # Work in progress

    def validate_dates(self, sheet_name, column, date_list):
        nrow = 0
        for date in date_list:
            nrow += 1
            correct_date1 = search(r"^\d{4}-\d{2}-\d{2}T.*", date)  # 2024-12-20T10:23:21+00:00
            if not correct_date1:
                correct_date2 = search(r"^\d{4}-\d{2}-\d{2}$", date)  # 2024-12-20
                if not correct_date2:
                    correct_date3 = search(r"^\d{4}-\d{2}$", date)  # 2024-12
                    if not correct_date3:
                        correct_date4 = search(r"^\d{4}$", date)  # 2024
                        if not correct_date4:
                            self.logs.append(
                                f"CHECK WARNING - The {sheet_name} sheet, *{column}* column, row {nrow} is incorrectly formatted.")

    def validate_formats(self, sheet_name):
        try:
            # Get rid of empty rows (all "None" or "NaN")
            self.sheet_df = self.sheet_df.dropna(axis='index', how='all')
            # Format Checks specific for Study Sheet
            if sheet_name == "Study":
                # Are Study IDs unique?
                # Bellow line not working for vitis because first col in Study sheet is 'Investigation unique ID' instead of 'Study unique ID')
                # if len(self.sheet_df.iloc[:, 0].unique()) != len(self.sheet_df.iloc[:, 0]):
                if len(self.sheet_df['Study unique ID'].unique()) != len(self.sheet_df['Study unique ID']):
                    self.logs.append(
                        f"CHECK FAILED - The {sheet_name} sheet, *Study unique ID* column, identifiers must be unique.")
                    self.run = False

                # # Are Dates properly formated?
                # start_dates_list = list(self.sheet_df.iloc[:, 4]) 
                date_list = list(self.sheet_df['Start date of study'][1:])
                date_list = [str(date) for date in date_list]
                self.validate_dates(sheet_name, "Start date of study", date_list)
                # end_dates_list = list(self.sheet_df.iloc[:, 5])
                date_list = list(self.sheet_df['End date of study'][1:])
                date_list = [str(date) for date in date_list]
                self.validate_dates(sheet_name, "End date of study", date_list)

        except ValueError:
            self.logs.append("CHECK FAILED - The Study sheet cannot be opened.")
            self.run = False

        # sheet_format = self.sheet_df.dtypes
        # TODO - (Or not) Doesn't validate if "ODS" format since dataframe is built from nested list
        # if "valid_formats" in self.valid_structure[sheet_name]:
        # if str(list(sheet_format)) in self.valid_structure[sheet_name]['valid_formats']:
        # self.logs.append(
        # f"CHECK PASSED - The {sheet_name} sheet has a valid format (properly formatted fields). Not checked.")
        # else:
        # self.logs.append(
        # f"CHECK WARNING - The {sheet_name} sheet has invalid formats (some fields are incorrectly formatted). Not checked.")
        # self.run = True

    def check_sheet(self, sheet_name):
        try:

            header = self.load_worksheet(sheet_name)
            self.validate_headers(header, sheet_name)
            self.validate_data(sheet_name)
            self.validate_formats(sheet_name)

        except ValueError:
            self.logs.append(f"CHECK FAILED - The {sheet_name} sheet cannot be opened.")
            self.run = False

    # The input file should end in .xlsx, .xls or .ods
    # Additional excel-like files which may be considered (older versions): .xlsm; .xlsb; .xml;
    # .xltx; .xlt; .xltm; .xlam; .xlc; xld; .xlk; .xlw; .xlr.
    def run_miappe_validator(self):

        if self.run:
            self.check_input_file()

        # Skip Data Value
        if self.run:
            for sheet in list(self.sheetsList)[:-1]:
                if self.run and sheet in self.valid_structure:
                    self.check_sheet(sheet)

        # Append File is Valid if self.run reaches the end as True
        if self.run:
            self.logs.append(" - THE INPUT FILE IS VALID - ")
        else:
            self.logs.append(" - THE INPUT FILE IS INVALID - ")

        # Send the logs to the Node process
        print(self.logs)
        sys.stdout.flush()

        print(datetime.now() - startTime)
        return self.logs

# :)
