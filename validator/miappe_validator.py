# Script to read and validate input MIAPPE Compliant Excel file.

# Read required packages
from pyexcel_ods3 import get_data
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
        if len(self.valid_sheets) < len(valid_sheet_names[:-1]):
            self.invalid_sheets = [sheet for sheet in self.sheetsList if sheet not in valid_sheet_names ]
            self.logs.append(
                    "CHECK FAILED - The input file has " + str(len(self.valid_sheets)) + 
                    " valid input sheets, which is less than the minimum 11 valid sheets required: Investigation, Study, Person, Data file, Biological Material, Sample, Observation Unit, Environment, Factor/Exp. Factor, Observed Variable, Event")
            self.logs.append(
                f"CHECK FAILED - The input file has {len(self.invalid_sheets)} " +
                     f"invalid input worksheets. Correct <<{'>>, <<'.join(self.invalid_sheets)}>>")

            self.run = False
        else:
            if len(self.sheetsList) >= len(valid_sheet_names[:-1]):
                self.logs.append(
                    f"CHECK PASSED - The input file has the minimum required {len(valid_sheet_names[:-1])} valid sheet names.")
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
            self.logs.append(list(self.complete_excel.keys())[0])
            return [ele.replace('*', '') for ele in list(self.sheet_df)]
        else:
            self.sheet_df = pd.read_excel(self.complete_excel, self.name_of_similar_sheet(sheet_name))
            self.logs.append(self.sheet_df.columns[0])
            # Remove '*' characters, which indicate mandatory columns to fill
            return [ele.replace('*', '') for ele in list(self.sheet_df)]

    def validate_headers(self, header, sheet_name):
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

    def validate_data(self, sheet_name):
        if 'can_be_empty' in self.valid_structure[sheet_name]:
            if not self.valid_structure[sheet_name]['can_be_empty']:
                if len(self.sheet_df.index) != 0:
                    for mandatory_column in self.valid_structure[sheet_name]['mandatory_columns']:
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
            # This means that the Excel is the template from MIAPPE Github

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
                    f"CHECK PASSED - The {sheet_name} sheet has a valid format (properly formatted fields).")
            else:
                self.logs.append(
                    f"CHECK WARNING - The {sheet_name} sheet has invalid formats (some fields are incorrectly formatted).")
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
    # REDO SECTION TO ALLOW MIAPPE TEMPLATE (TRANSPOSED VERSION)
    def CheckInvestigationSheet(self):
        self.logs.append("investigation" + str(datetime.now() - startTime))
        # Check Investigation Sheet Header
        try:
            sheet_name = "Investigation"
            investigation_header = None
            if self.filetype == "od":
                self.sheet_df = self.complete_excel[self.name_of_similar_sheet(sheet_name)]
                investigation_header = [ele.replace('*', '') for ele in list(self.sheet_df)]
                self.logs.append(list(self.complete_excel.keys())[0])
            else:
                self.sheet_df = pd.read_excel(self.complete_excel, self.name_of_similar_sheet(sheet_name))
                self.logs.append(self.sheet_df.columns[0])
                # Remove '*' characters, which indicate mandatory columns to fill
                investigation_header = [ele.replace('*', '') for ele in list(self.sheet_df)]

            valid_investigation_header1 = ["Investigation unique ID", "Investigation title", "Investigation description",
                                          "Submission date", "Public release date", "License", "MIAPPE version",
                                          "Associated publication"]
            valid_investigation_header2 = ["Field", "Value", "Definition", "Example", "Format"]
            valid_investigation_header3 = ["Field", "Value"]

            if investigation_header == valid_investigation_header1:
                self.logs.append("CHECK PASSED - The Investigation sheet has a valid header (column name/number).")

                # valid_investigation_formats_dic = {1: ["dtype('O')"], 2: "dtype('O')", 3: "dtype('O')", 4: ["dtype('<M8[ns]')", "dtype('float64')"],
                #                                  5: ["dtype('<M8[ns]')", "dtype('float64')"], 6: ["dtype('O')", "dtype('float64')"],
                #                                  7: ["dtype('O')", "dtype('float64')"], 8: ["dtype('O')", "dtype('float64')"]}
                
                investigation_format = self.sheet_df.dtypes
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

            # This means that the Excel is the template from MIAPPE Github (or modified to keep only two first columns)
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

    #  -  Check Study Sheet  -

    def CheckStudySheet(self):
        self.logs.append("study" + str(datetime.now() - startTime))
        # Check Study Sheet Header
        try:
            sheet_name = "Study"
            header = None
            if self.filetype == "od":
                self.sheet_df = self.complete_excel[self.name_of_similar_sheet(sheet_name)]
                header = [ele.replace('*', '') for ele in list(self.sheet_df)]
                self.logs.append(list(self.complete_excel.keys())[0])
            else:
                self.sheet_df = pd.read_excel(self.complete_excel, self.name_of_similar_sheet(sheet_name))
                self.logs.append(self.sheet_df.columns[0])
                # Remove '*' characters, which indicate mandatory columns to fill
                header = [ele.replace('*', '') for ele in list(self.sheet_df)]

            # Valid Study sheet Headers:
            valid_study_header1 = ["Study unique ID", "Study title", "Study description", "Start date of study",
                               "End date of study", "Contact institution", "Geographic location (country)",
                               "Experimental site name", "Geographic location (latitude)",
                               "Geographic location (longitude)", "Geographic location (altitude)",
                               "Description of the experimental design", "Type of experimental design",
                               "Observation unit level hierarchy", "Observation unit description",
                               "Description of growth facility", "Type of growth facility", "Cultural practices",
                               "Map of experimental design"]
            valid_study_header2 = ["Investigation unique ID", "Study unique ID", "Study title", "Study description",
                               "Start date of study", "End date of study", "Contact institution",
                               "Geographic location (country)", "Experimental site name", "Geographic location (latitude)",
                               "Geographic location (longitude)", "Geographic location (altitude)",
                               "Description of statistical design", "Type of statistical design",
                               "Observation unit level hierarchy", "Observation unit description",
                               "Description of growth facility", "Type of growth facility", "Cultural practices",
                               "Map of experimental design"]
            # For vitis file to work, Investigation title column added
            valid_study_header3 = ["Investigation unique ID", "Investigation title", "Study unique ID", "Study title",
                                "Study description", "Start date of study", "End date of study", "Contact institution",
                               "Geographic location (country)", "Experimental site name", "Geographic location (latitude)",
                               "Geographic location (longitude)", "Geographic location (altitude)",
                               "Description of statistical design", "Type of statistical design",
                               "Observation unit level hierarchy", "Observation unit description",
                               "Description of growth facility", "Type of growth facility", "Cultural practices",
                               "Map of experimental design"]

            if header == valid_study_header1 or header == valid_study_header2 or header == valid_study_header3:
                self.logs.append("CHECK PASSED - The Study sheet has a valid header (column name/number).")
            else:
                self.logs.append("CHECK FAILED - The Study sheet has an invalid header (column name/number).")
                self.run = False

        except ValueError:
            self.logs.append("CHECK FAILED - The Study sheet cannot be opened.")
            self.run = False

    # Deprecated
    #  -  Check Person Sheet  -
    def CheckPersonSheet(self):
        self.logs.append(datetime.now() - startTime)
        # Check Person Sheet Header
        try:
            self.sheet_df = pd.read_excel(self.input_file, 'Person')
            # Remove '*' characters, which indicate mandatory columns to fill
            person_header = [ele.replace('*', '') for ele in list(self.sheet_df)]

            # Valid Person sheet Headers:
            valid_person_header1 = ["Person name", "Person email", "Person ID", "Person role", "Person affiliation"]
            valid_person_header2 = ["Study unique ID", "Person name", "Person email", "Person ID", "Person role",
                                    "Person affiliation"]
            valid_person_header3 = ["Field", "Study unique ID", "Person name*", "Person email", "Person ID", "Person role*",
                                    "Person affiliation*"]

            if person_header == valid_person_header1 or person_header == valid_person_header2:
                self.logs.append("CHECK PASSED - The Person sheet has a valid header (column name/number).")
                # Give error if Person sheet is empty
                if len(self.sheet_df.index) != 0:
                    # Person sheet - Checks if mandatory columns have values (at least in the first position)
                    if pd.isna(self.sheet_df.iloc[0, 0]) == True:
                        self.logs.append("CHECK FAILED - The Study unique ID column (Person sheet) is mandatory.")
                        self.run = False
                    if pd.isna(self.sheet_df.iloc[0,1]) == True:
                        self.logs.append("CHECK FAILED - The Person name* column (Person sheet) is mandatory.")
                        self.run = False
                    if pd.isna(self.sheet_df.iloc[0,4]) == True:
                        self.logs.append("CHECK FAILED - The Person role* column (Person sheet) is mandatory.")
                        self.run = False
                    if pd.isna(self.sheet_df.iloc[0,5]) == True:
                        self.logs.append("CHECK FAILED - The Person affiliation* column (Person sheet) is mandatory.")
                        self.run = False
                else:
                    self.logs.append("CHECK FAILED - The Person Sheet is empty.")
                    self.run = False
            # This means that the Excel is the template from MIAPPE Github
            elif person_header == valid_person_header3:
                # Delete first column and then first three rows of the person dataframe
                self.sheet_df.drop(["Definition", "Example", "Format"], axis = 0, inplace = True)
                self.sheet_df.drop("Field", axis = 1, inplace = True)
                # Give error if Person sheet is empty
                if len(self.sheet_df.index) != 0:
                # Person sheet - Checks if mandatory columns have values (at least in the first position)
                    if pd.isna(self.sheet_df.iloc[0, 0]) == True:
                        self.logs.append("CHECK FAILED - The Study unique ID column (Person sheet) is mandatory.")
                        self.run = False
                    if pd.isna(self.sheet_df.iloc[0,1]) == True:
                        self.logs.append("CHECK FAILED - The Person name* column (Person sheet) is mandatory.")
                        self.run = False
                    if pd.isna(self.sheet_df.iloc[0,4]) == True:
                        self.logs.append("CHECK FAILED - The Person role* column (Person sheet) is mandatory.")
                        self.run = False
                    if pd.isna(self.sheet_df.iloc[0,5]) == True:
                        self.logs.append("CHECK FAILED - The Person affiliation* column (Person sheet) is mandatory.")
                        self.run = False
                else:
                    self.logs.append("CHECK FAILED - The Person Sheet is empty.")
                    self.run = False
            else:
                self.logs.append("CHECK FAILED - The Person sheet has an invalid header (column name/number).")
                self.run = False

            # Cleaning "\n" characters from the dataframe
            # self.sheet_df.replace({'\n': ''}, regex=True)

            # Check Person field formats per column
            # person_format = self.sheet_df.dtypes
            # self.logs.append(person_format)

            self.logs.append(
            "CHECK PASSED - The Person sheet has valid columns (properly formatted fields).")

        except ValueError:
            self.logs.append("CHECK FAILED - The Person sheet cannot be opened.")
            self.run = False

    # Deprecated
    #  -  Check Data File Sheet  -
    def CheckDatafileSheet(self):
        # Check Data File Sheet Header (In MIAPPE specs it is named Data File)
        try:
            sheet_name = "Data file"
            self.sheet_df = pd.read_excel(self.complete_excel, self.name_of_similar_sheet(sheet_name))
            # Remove '*' characters, which indicate mandatory columns to fill
            datafile_header = [ele.replace('*', '') for ele in list(self.sheet_df)]

            # Valid Data File sheet Headers:
            valid_datafile_header1 = ["Data file link", "Data file description", "Data file version"]
            valid_datafile_header2 = ["Study unique ID", "Data file link", "Data file description", "Data file version"]

            if datafile_header == valid_datafile_header1 or datafile_header == valid_datafile_header2:
                self.logs.append("CHECK PASSED - The Data File sheet has a valid header (column name/number).")
            else:
                self.logs.append("CHECK FAILED - The Data File sheet has an invalid header (column name/number).")
                self.run = False
                #sys.exit(" - ERROR - Invalid Header in Data File Sheet - ")

            # Cleaning "\n" characters from the dataframe
            self.sheet_df.replace({'\n': ''}, regex=True)

            # Check Data Field field formats per column
            datafile_format = self.sheet_df.dtypes

            valid_datafile_formats = ["[dtype('O'), dtype('O'), dtype('O'), dtype('O')]",
                                      "[dtype('O'), dtype('O'), dtype('O'), dtype('float64')]"]
            # Format 1 - All mandatory fields filled
            # Format 2 - Data file version can be a float ('float64')

            if str(list(datafile_format)) in valid_datafile_formats:
                self.logs.append("CHECK PASSED - The Data File sheet has a valid format (properly formatted fields).")
            else:
                self.logs.append("CHECK FAILED - The Data File sheet has a invalid format (some fields are incorrectly formatted).")
                self.run = False

        except ValueError:
            self.logs.append("CHECK FAILED - The Data file sheet cannot be opened.")
            self.run = False

    # Deprecated
    #  -  Check Biological Material Sheet  -
    def CheckBiologicalMaterialSheet(self):
        # Check Biological Material Sheet Header
        try:
            sheet_name = "Biological Material"
            self.sheet_df = pd.read_excel(self.complete_excel, self.name_of_similar_sheet(sheet_name))
            # Remove '*' characters, which indicate mandatory columns to fill
            biomaterial_header = [ele.replace('*', '') for ele in list(self.sheet_df)]

            # Valid Biological Material sheet Headers:
            valid_biomaterial_header1 = ["Biological material ID", "Organism", "Genus", "Species", "Infraspecific name",
                                        "Biological material latitude", "Biological material longitude",
                                        "Biological material altitude", "Biological material coordinates uncertainty",
                                        "Biological material preprocessing",
                                        "Material source ID (Holding institute/stock centre, accession)",
                                        "Material source DOI", "Material source latitude", "Material source longitude",
                                        "Material source altitude", "Material source coordinates uncertainty",
                                        "Material source description"]
            valid_biomaterial_header2 = ["Study unique ID", "Biological material ID", "Organism", "Genus", "Species",
                                        "Biological material latitude", "Biological material longitude",
                                        "Biological material altitude", "Biological material coordinates uncertainty",
                                        "Biological material preprocessing", "Material source ID", "Material source DOI",
                                        "Material source latitude", "Material source longitude", "Material source altitude",
                                        "Material source coordinates uncertainty", "Material source description"]

            if biomaterial_header == valid_biomaterial_header1 or biomaterial_header == valid_biomaterial_header2:
                self.logs.append("CHECK PASSED - The Biological Material sheet has a valid header (column name/number).")
            else:
                self.logs.append("CHECK FAILED - The Biological Material sheet has an invalid header (column name/number).")
                self.run = False
                #sys.exit(" - ERROR - Invalid Header in Biological Material Sheet - ")

            # Cleaning "\n" characters from the dataframe
            self.sheet_df.replace({'\n': ''}, regex=True)

            # Check Biological Material field formats per column
            biomaterial_format = self.sheet_df.dtypes

            valid_biomaterial_formats = ["[dtype('O'), dtype('O'), dtype('O'), dtype('float64'), dtype('float64'), dtype('float64'), dtype('float64'), dtype('float64'), dtype('float64'), dtype('float64'), dtype('float64'), dtype('float64'), dtype('float64'), dtype('float64'), dtype('float64'), dtype('float64'), dtype('float64')]",
                                         "[dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('float64'), dtype('float64'), dtype('O'), dtype('float64'), dtype('float64'), dtype('O'), dtype('O'), dtype('float64'), dtype('float64'), dtype('float64'), dtype('float64'), dtype('O')]",
                                         "[dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('float64'), dtype('float64'), dtype('O'), dtype('float64'), dtype('float64'), dtype('O'), dtype('float64'), dtype('float64'), dtype('float64'), dtype('float64'), dtype('float64'), dtype('O')]",
                                         "[dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('float64'), dtype('float64'), dtype('float64'), dtype('O'), dtype('O'), dtype('float64'), dtype('float64'), dtype('float64'), dtype('float64'), dtype('float64'), dtype('float64'), dtype('float64')]"]
            # Format 1 - Mandatory fields must have valid formats, while the rest can be empty ('float64')
            # Format 2 - Rice file
            # Format 3 - Valid file
            # Format 4 - Vitis file

            if str(list(biomaterial_format)) in valid_biomaterial_formats:
                self.logs.append("CHECK PASSED - The Biological Material sheet has a valid format (properly formatted fields).")
            else:
                self.logs.append(
                    "CHECK WARNING - The Biological Material sheet has invalid formats (some fields are incorrectly formatted).")
                self.run = False

        except ValueError:
            self.logs.append("CHECK FAILED - The Biological Material sheet cannot be opened.")
            self.run = False

    # Deprecated
    #  -  Check Event Sheet  -
    def CheckEventSheet(self):
        # Check Event Sheet Header
        try:
            self.sheet_df = pd.read_excel(self.input_file, 'Event')
            # Remove '*' characters, which indicate mandatory columns to fill
            event_header = [ele.replace('*', '') for ele in list(self.sheet_df)]

            # Valid Event sheet Headers:
            valid_event_header1 = ["Event type", "Event accession number", "Event description", "Event date"]
            valid_event_header2 = ["Study unique ID", "Observation unit ID", "Event type", "Event acession number",
                               "Event description", "Event date"]
            # Custom MIAPPE (header2) misspells "accession" with "acession"

            if event_header == valid_event_header1 or event_header == valid_event_header2:
                self.logs.append("CHECK PASSED - The Event sheet has a valid header (column name/number).")
            else:
                self.logs.append("CHECK FAILED - The Event sheet has an invalid header (column name/number).")
                self.run = False
                #sys.exit(" - ERROR - Invalid Header in Event Sheet - ")

            # Cleaning "\n" characters from the dataframe
            self.sheet_df.replace({'\n': ''}, regex=True)

            # Check Event field formats per column
            event_format = self.sheet_df.dtypes

            # Skip format validation if this sheet is empty
            if len(self.sheet_df.index) != 0:
                valid_event_formats = ["[dtype('O'), dtype('float64'), dtype('O'), dtype('float64'), dtype('float64'), dtype('<M8[ns]')]",
                                       "[dtype('O'), dtype('float64'), dtype('O'), dtype('float64'), dtype('float64'), dtype('O')]",
                                       "[dtype('O'), dtype('O'), dtype('O'), dtype('float64'), dtype('O'), dtype('O')]",
                                       "[dtype('O'), dtype('O'), dtype('O'), dtype('float64'), dtype('O'), dtype('<M8[ns]')]",
                                       "[dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('<M8[ns]')]",
                                       "[dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('O')]"]
                # Format 1 - Mandatory fields must have valid formats, while the rest can be empty ('float64')
                # Format 2 - Equal to 1, but date is interpreted as object ('O')
                # Format 3 - Event acession number left empty
                # Format 4 - Equal to 3, but date is interpreted as object ('O')
                # Format 5 - All fields are filled
                # Format 6 - Equal to 3 but date is interpreted as object ('O')

                if str(list(event_format)) in valid_event_formats:
                    self.logs.append("CHECK PASSED - The Event sheet has a valid format (properly formatted fields).")
                else:
                    self.logs.append("CHECK FAILED - The Event sheet has a invalid format (some fields are incorrectly formatted).")
                    self.run = False
                    #sys.exit(" - ERROR - Invalid Field Formats in Event Sheet - ")
            else:
                self.logs.append("CHECK WARNING - The Event sheet is empty (no format check applied).")

        except ValueError:
            self.logs.append("CHECK FAILED - The Event sheet cannot be opened.")
            self.run = False

    # The input file should end in .xlsx, .xls or .ods
    # Additional excel-like files which may be considered (older versions): .xlsm; .xlsb; .xml;
    # .xltx; .xlt; .xltm; .xlam; .xlc; xld; .xlk; .xlw; .xlr.
    def run_miappe_validator(self):

        if self.run == True:
            self.check_input_file()
        if self.run == True:
            self.CheckInvestigationSheet()
            # self.check_sheet('Investigation')

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

        with open(r'miappe_validator_logs.txt', 'w') as log:
            for item in self.logs:
                log.write("%s\n" % item)

        # Send the logs to the Node process

        print(self.logs)
        sys.stdout.flush()

        print(datetime.now() - startTime)
        return self.logs


    '''
    # Might use to go through the sheets and simplify duplicate code
    
    for sheet in sheetsList:
        print(sheet)
        sheet_df = pd.read_excel(input_file, sheet)
        print(sheet_df)
    
    
    
    # In node.js code
    
    const spawn = require("child_process").spawn;
    const pythonProcess = spawn('python',["path/to/script.py", arg1]);
    
    # In the python script
    
    import sys
    
    arg1 = sys.argv[1]
    
    # print(dataToSendBack)
    sys.stdout.flush()
    
    
    # Back in node
    
    pythonProcess.stdout.on('data', (data) => {
        // Do something with this data: print text box error message in OntoBrAPI specifying what went wrong.
    });
    '''

