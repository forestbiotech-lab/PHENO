# Script to read and validate input MIAPPE Compliant Excel file.

# Read required packages
from pyexcel_ods3 import get_datas
import pandas as pd
import json
import sys
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
        if len(self.valid_sheets) < (len(valid_sheet_names[:-1]) -1 ) and ("Exp. Factor" in self.valid_sheets and "Factor" in self.valid_sheets): # It's [:1] to ignore Data value, and -1 because Factor/Exp. Factor redundancy
            self.invalid_sheets = [sheet for sheet in self.sheetsList if sheet not in valid_sheet_names ]
            self.logs.append(
                    "CHECK FAILED - The input file has " + str(len(self.valid_sheets)) + 
                    " valid input sheets, which is less than the minimum 11 valid sheets required: Investigation, Study, Person, Data file, Biological Material, Sample, Observation Unit, Environment, Factor/Exp. Factor, Observed Variable, Event")
            self.logs.append(
                f"CHECK FAILED - The input file has {len(self.invalid_sheets)} " +
                     f"invalid input worksheets. Correct the worksheet &lt;&lt;{'&gt;&gt;, &lt;&lt;'.join(self.invalid_sheets)}&gt;&gt;")

            self.run = False
        else:
            if len(self.sheetsList) >= (len(valid_sheet_names[:-1]) -1 ):
                self.logs.append(
                    f"CHECK PASSED - The input file has the minimum required {(len(valid_sheet_names[:-1]) -1 )} valid sheet names.")
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
        if self.filetype == "od":
            self.sheet_df = self.complete_excel[sheet_name].drop(0)
            self.sheet_df = self.sheet_df.reset_index(drop=True)
        else:
            self.sheet_df = pd.read_excel(self.complete_excel, self.name_of_similar_sheet(sheet_name))
            # Remove '*' characters, which indicate mandatory columns to fill
        
        return [ele.replace('*', '') for ele in list(self.sheet_df)]

    # Checks if headers are valid
    def validate_headers(self, header, sheet_name):
        if "valid_header1" in self.valid_structure[sheet_name] and "valid_header2" in self.valid_structure[sheet_name]:
            if (header == self.valid_structure[sheet_name]['valid_header1'] or
                    header == self.valid_structure[sheet_name]['valid_header2']):
                self.logs.append(f'CHECK PASSED - The {sheet_name} sheet has a valid header (column name/number).')
                self.validate_data(sheet_name)

            elif header == self.valid_structure[sheet_name]['valid_header3'] and sheet_name == "Person":
                ###### Person specific??????
                # Delete first column and then first three rows of the person dataframe
                self.sheet_df.drop(["Definition", "Example", "Format"], axis=0, inplace=True)
                self.sheet_df.drop("Field", axis=1, inplace=True)

            elif "valid_header3" in self.valid_structure[sheet_name]:
                if header == self.valid_structure[sheet_name]['valid_header3']:
                    # Is used in Study for vitis exception which will be removed.
                    self.logs.append(f'CHECK PASSED - The {sheet_name} sheet has a valid header (column name/number).')
                    self.validate_data(sheet_name)
            else:
                self.logs.append(f"CHECK FAILED - The {sheet_name} sheet has an invalid header (column name/number).")
                self.run = False

    # Checks if mandatory columns are filled
    def validate_data(self, sheet_name):
        if 'can_be_empty' in self.valid_structure[sheet_name]:
            if not self.valid_structure[sheet_name]['can_be_empty']:
                if len(self.sheet_df.index) != 0:
                    for mandatory_column in self.valid_structure[sheet_name]['mandatory_columns']:
                        # It needs to exist, if not the header would had given error previously
                        if mandatory_column in self.sheet_df:
                            if pd.isna(self.sheet_df[mandatory_column][0]):
                                self.logs.append(
                                    f"CHECK FAILED - The {mandatory_column} column ({sheet_name} sheet) is mandatory.")
                                self.run = False
                        elif mandatory_column + "*" in self.sheet_df:
                            if pd.isna(self.sheet_df[mandatory_column + "*"][0]):
                                self.logs.append(
                                    f"CHECK FAILED - The {mandatory_column} column ({sheet_name} sheet) is mandatory.")
                                self.run = False
                else:
                    self.logs.append(f"CHECK FAILED - The {sheet_name} Sheet is empty.")
                    self.run = False

    # Work in progress, maybe drop it
    def validate_dtypes(self, sheet_name):
        sheet_format = self.sheet_df.dtypes
        # TODO - (Or not) Doesn't validate if "ODS" format since dataframe is built from nested list
        if "valid_formats" in self.valid_structure[sheet_name]:
            # Format 1 - Mandatory fields must have valid formats, while the rest can be empty ('float64')
            # Format 2 - Rice file
            # Format 3 - Valid file
            # Format 4 - Vitis file
            if str(list(sheet_format)) in self.valid_structure[sheet_name]['valid_formats']:
                self.logs.append(
                    f"CHECK PASSED - The {sheet_name} sheet has a valid format (properly formatted fields). Not checked.")
            else:
                self.logs.append(
                    f"CHECK WARNING - The {sheet_name} sheet has invalid formats (some fields are incorrectly formatted). Not checked.")
                self.run = True

    def check_sheet(self, sheet_name):
        try:

            header = self.load_worksheet(sheet_name)
            self.validate_headers(header, sheet_name)
            self.validate_dtypes(sheet_name)

        except ValueError:
            self.logs.append(f"CHECK FAILED - The {sheet_name} sheet cannot be opened.")
            self.run = False

    #  -  Check Investigation Sheet  -
    def CheckInvestigationSheet(self):
        # self.logs.append("investigation" + str(datetime.now() - startTime))
        # Check Investigation Sheet Header
        try:
            sheet_name = "Investigation"
            if self.filetype == "od":
                self.sheet_df = self.complete_excel[sheet_name]
            else:
                self.sheet_df = pd.read_excel(self.complete_excel, sheet_name)
                
            # Remove '*' characters, which indicate mandatory columns to fill
            investigation_header = [ele.replace('*', '') for ele in list(self.sheet_df)]

            valid_investigation_header1 = ["Investigation unique ID", "Investigation title", "Investigation description",
                                          "Submission date", "Public release date", "License", "MIAPPE version",
                                          "Associated publication"]
            valid_investigation_header2 = ["Field", "Value", "Definition", "Example", "Format"]
            valid_investigation_header3 = ["Field", "Value"]

            # Normal Header
            if investigation_header == valid_investigation_header1:
                self.logs.append("CHECK PASSED - The Investigation sheet has a valid header (column name/number).")

                # valid_investigation_formats_dic = {1: ["dtype('O')"], 2: "dtype('O')", 3: "dtype('O')", 4: ["dtype('<M8[ns]')", "dtype('float64')"],
                #                                  5: ["dtype('<M8[ns]')", "dtype('float64')"], 6: ["dtype('O')", "dtype('float64')"],
                #                                  7: ["dtype('O')", "dtype('float64')"], 8: ["dtype('O')", "dtype('float64')"]}
                
                # investigation_format = self.sheet_df.dtypes
                #self.logs.append(investigation_format)
                
                # Checks if mandatory columns have values (at least in the first position)
                if pd.isna(self.sheet_df.iloc[0, 0]) == True:
                    self.logs.append("CHECK FAILED - The Investigation ID* (Investigation sheet) is required.")
                    self.run = False
                if pd.isna(self.sheet_df.iloc[0,1]) == True:
                    self.logs.append("CHECK FAILED - The Investigation Title* (Investigation sheet) is required.")
                    self.run = False
                if pd.isna(self.sheet_df.iloc[0,2]) == True:
                    self.logs.append("CHECK FAILED - The Investigation Description* (Investigation sheet) is required.")
                    self.run = False
                if pd.isna(self.sheet_df.iloc[0,6]) == True:
                    self.logs.append("CHECK FAILED - The MIAPPE version* (Investigation sheet) is required.")
                    self.run = False

            # This means that the Excel is the template from MIAPPE Github (or modified by user to keep only two first columns)
            elif investigation_header == valid_investigation_header2 or investigation_header == valid_investigation_header3:
                # Check if Rows are well named
                if self.sheet_df.iloc[1:, 0] == valid_investigation_header1:
                    self.logs.append("CHECK PASSED - The Investigation sheet has a valid header (column name/number).")
                else:
                    self.logs.append("CHECK FAILED - The Investigation sheet has incorrect names in the Field.")
                    self.run = False

                # The transposed version Original Github
                # Check if mandatory fields within Investigation sheet exist (not NaN)
                if pd.isna(self.sheet_df.iloc[1,1]) == True:
                    self.logs.append("CHECK FAILED - The Investigation ID* (Investigation sheet) is required.")
                    self.run = False
                if pd.isna(self.sheet_df.iloc[2,1]) == True:
                    self.logs.append("CHECK FAILED - The Investigation Title* (Investigation sheet) is required.")
                    self.run = False
                if pd.isna(self.sheet_df.iloc[3,1]) == True:
                    self.logs.append("CHECK FAILED - The Investigation Description* (Investigation sheet) is required.")
                    self.run = False
                if pd.isna(self.sheet_df.iloc[7,1]) == True:
                    self.logs.append("CHECK FAILED - The MIAPPE Version* (Investigation sheet) is required.")
                    self.run = False

            else: 
                self.logs.append("CHECK FAILED - The Investigation sheet has an invalid header (column name/number).")
                self.run = False

            self.logs.append(
            "CHECK PASSED - The Investigation sheet has valid columns (properly formatted fields).")

        except ValueError:
            self.logs.append("CHECK FAILED - The Study sheet cannot be opened.")
            self.run = False

    #TODO
    #Check mandatory columns are filled (already checked in Investigation, check for the other ones)
    # Maybe check column formats, dtypes abandoned, because format needs to be informative of the column

    # The input file should end in .xlsx, .xls or .ods
    # Additional excel-like files which may be considered (older versions): .xlsm; .xlsb; .xml;
    # .xltx; .xlt; .xltm; .xlam; .xlc; xld; .xlk; .xlw; .xlr.
            
    def run_miappe_validator(self):

        if self.run == True:
            self.check_input_file()
        if self.run == True:
            self.CheckInvestigationSheet()

        # Skip Investigation and Data Value
        if self.run:
            for sheet in list(self.sheetsList)[1:-1]:
                if self.run and sheet in self.valid_structure:
                    self.check_sheet(sheet)

        # Write miappe_validator_logs file:
        # Append File is Valid if self.run reaches the end as True
        if self.run == True:
            self.logs.append(" - THE INPUT FILE IS VALID - ")
        else:
            self.logs.append(" - THE INPUT FILE IS INVALID - ")

        # Send the logs to the Node process
        print(self.logs)
        sys.stdout.flush()

        print(datetime.now() - startTime)
        return self.logs

# :)