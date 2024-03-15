# Script to read and validate input MIAPPE Compliant Excel file.

# Read required packages
import pandas as pd
import sys
# Check script execution time
from datetime import datetime

startTime = datetime.now()

#   ---   Define a Miappe_validator Class   ---

class Miappe_validator:

#   ---   Initiate class properties and check Input File extension  ---
    
    def __init__(self, input_file):
        self.logs = ["  --- OntoBrAPI - Input File Validity Report ---  "]
        self.run = True
        # Loads file
        self.input_file = input_file
        try:
            if self.input_file.lower().endswith(('.xlsx', '.xls', 'ods')):
                self.logs.append("CHECK PASSED - Valid input file extension")
                self.complete_excel = pd.ExcelFile(input_file)
                self.sheetsList = self.complete_excel.sheet_names
            else:
                self.logs.append("CHECK FAILED - Invalid input file extension")
                self.run = False
        except FileNotFoundError:
            self.logs = ["CHECK FAILED - Invalid input file"]
            self.run = False


    #  -  Check sheet number & sheet names  -
            
    def check_input_file(self):
        # These are all valid sheet names for a MIAPPE compliant excel file
        valid_sheet_names = ["Investigation", "Study", "Person", "Data file", "Biological Material", "Sample",
                             "Observation Unit", "Environment", "Factor", "Observed Variable", "Event"]

        # Check the number of input sheet names that are valid or not
        self.valid_sheets = [i for i in self.sheetsList if i in valid_sheet_names]
        if len(self.valid_sheets) < 11:
            self.logs.append(
                    "CHECK FAILED - The input file has " + str(len(self.valid_sheets)) + 
                    " valid input sheets, which is less than the minimum 11 valid sheets required: Investigation, Study, Person, Data file, Biological Material, Sample, Observation Unit, Environment, Factor, Observed Variable, Event")
            self.run = False
            #TODO keep running only checking the methods for the sheets that exist.
        else:
            if len(self.sheetsList) == 11:
                self.logs.append(
                    "CHECK PASSED - The input file has the minimum required 11 valid sheet names.")
            else:
                self.logs.append(
                    "CHECK WARNING - The input file has " + str(len(self.sheetsList)) + 
                    " sheets, which is more than the minimum 11 valid sheets required. Additional sheets may be discarded.")


    #  -  Check Investigation Sheet  -
    # REDO SECTION TO ALLOW MIAPPE TEMPLATE (TRANSPOSED VERSION)

    def CheckInvestigationSheet(self):
        self.logs.append(datetime.now() - startTime)
        # Check Investigation Sheet Header
        try:
            self.sheet_df = pd.read_excel(self.complete_excel, 'Investigation')
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
                self.logs.append(investigation_format)
                self.logs.append(self.sheet_df.iloc[0, 0])
                
                # Checks that columns which require mandatory values are filled

                if pd.isna(self.sheet_df.iloc[1, 1]) == True:
                    self.logs.append("CHECK FAILED - The Investigation ID* (Investigation sheet) is required.")
                    self.run = False
                if pd.isna(self.sheet_df.iloc[1,2]) == True:
                    self.logs.append("CHECK FAILED - The Investigation Title* (Investigation sheet) is required.")
                    self.run = False
                if pd.isna(self.sheet_df.iloc[1,3]) == True:
                    self.logs.append("CHECK FAILED - The Investigation Description* (Investigation sheet) is required.")
                    self.run = False
                # if str(investigation_format[3]) not in valid_investigation_formats_dic['col4']:
                    # self.logs.append("CHECK WARNING - The Submission Date (Investigation sheet) is incorrectly formated.")
                # if str(investigation_format[4]) not in valid_investigation_formats_dic['col5']:
                    # self.logs.append("CHECK WARNING - The Public Release date (Investigation sheet) is incorrectly formated.")
                # if str(investigation_format[5]) not in valid_investigation_formats_dic['col6']:
                    # self.logs.append("CHECK FAILED - The License (Investigation sheet) is incorrectly formated.")
                    # self.run = False
                if pd.isna(self.sheet_df.iloc[1,7]) == True:
                    self.logs.append("CHECK FAILED - The MIAPPE version* (Investigation sheet) is required.")
                    self.run = False
                # if str(investigation_format[7]) not in valid_investigation_formats_dic['col8']:
                    # self.logs.append("CHECK FAILED - The Associatied publication (Investigation sheet) is incorrectly formated.")
                    # self.run = False

            elif investigation_header == valid_investigation_header2 or investigation_header == valid_investigation_header3:
                # Check if Rows are well named
                if self.sheet_df.iloc[1:, 0] == valid_investigation_header1:
                    self.logs.append("CHECK PASSED - The Investigation sheet has a valid header (column name/number).")
                else:
                    self.logs.append("CHECK FAILED - The Investigation sheet has incorrect names used in the first column.")
                    self.run = False

                #Check if mandatory fields within Investigation sheet exist (not NaN)
                if pd.isna(self.sheet_df.iloc[1,1]) == True:
                    self.logs.append("CHECK FAILED - The Investigation ID* (Investigation sheet) is required.")
                    self.run = False
                if pd.isna(self.sheet_df.iloc[2,1]) == True:
                    self.logs.append("CHECK FAILED - The Investigation ID* (Investigation sheet) is required.")
                    self.run = False
                if pd.isna(self.sheet_df.iloc[3,1]) == True:
                    self.logs.append("CHECK FAILED - The Investigation ID* (Investigation sheet) is required.")
                    self.run = False
                if pd.isna(self.sheet_df.iloc[7,1]) == True:
                    self.logs.append("CHECK FAILED - The Investigation ID* (Investigation sheet) is required.")
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
        self.logs.append(datetime.now() - startTime)
        # Check Study Sheet Header
        try:
            self.sheet_df = pd.read_excel(self.input_file, 'Study')
            # Remove '*' characters, which indicate mandatory columns to fill
            study_header = [ele.replace('*', '') for ele in list(self.sheet_df)]

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
            # For vitis file to work, Investigation title col added
            valid_study_header3 = ["Investigation unique ID", "Investigation title", "Study unique ID", "Study title",
                                "Study description", "Start date of study", "End date of study", "Contact institution",
                               "Geographic location (country)", "Experimental site name", "Geographic location (latitude)",
                               "Geographic location (longitude)", "Geographic location (altitude)",
                               "Description of statistical design", "Type of statistical design",
                               "Observation unit level hierarchy", "Observation unit description",
                               "Description of growth facility", "Type of growth facility", "Cultural practices",
                               "Map of experimental design"]

            if study_header == valid_study_header1 or study_header == valid_study_header2 or study_header == valid_study_header3:
                self.logs.append("CHECK PASSED - The Study sheet has a valid header (column name/number).")
            else:
                self.logs.append("CHECK FAILED - The Study sheet has an invalid header (column name/number).")
                self.run = False

        except ValueError:
            self.logs.append("CHECK FAILED - The Study sheet cannot be opened.")
            self.run = False

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

            if person_header == valid_person_header1 or person_header == valid_person_header2:
                self.logs.append("CHECK PASSED - The Person sheet has a valid header (column name/number).")
            else:
                self.logs.append("CHECK FAILED - The Person sheet has an invalid header (column name/number).")
                self.run = False
                #sys.exit(" - ERROR - Invalid Header in Person Sheet - ")

            # Cleaning "\n" characters from the dataframe
            self.sheet_df.replace({'\n': ''}, regex=True)

            # Check Person field formats per column
            person_format = self.sheet_df.dtypes

            valid_person_formats = ["[dtype('O'), dtype('O'), dtype('float64'), dtype('float64'), dtype('O'), dtype('O')]",
                                    "[dtype('O'), dtype('O'), dtype('float64'), dtype('O'), dtype('O'), dtype('O')]",
                                    "[dtype('O'), dtype('O'), dtype('O'), dtype('float64'), dtype('O'), dtype('O')]",
                                    "[dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('O')]"]
            # Format 1 - Mandatory fields must have valid formats, while the rest can be empty ('float64')
            # Format 2 - Person email is missing
            # Format 3 - Person ID is missing
            # Format 2 - All fields are filled ('O')

            if str(list(person_format)) in valid_person_formats:
                self.logs.append("CHECK PASSED - The Person sheet has a valid format (properly formatted fields).")
            else:
                self.logs.append("CHECK FAILED - The Person sheet has a invalid format (some fields are incorrectly formatted).")
                self.run = False
                #sys.exit(" - ERROR - Invalid Field Formats in Person Sheet - ")

        except ValueError:
            self.logs.append("CHECK FAILED - The Person sheet cannot be opened.")
            self.run = False

    #  -  Check Data File Sheet  -

    def CheckDatafileSheet(self):
        # Check Data File Sheet Header (In MIAPPE specs it is named Data File)
        try:
            self.sheet_df = pd.read_excel(self.input_file, 'Data file')
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
                #sys.exit(" - ERROR - Invalid Field Formats in Data File Sheet - ")

        except ValueError:
            self.logs.append("CHECK FAILED - The Data file sheet cannot be opened.")
            self.run = False

    #  -  Check Biological Material Sheet  -

    def CheckBiologicalMaterialSheet(self):
        # Check Biological Material Sheet Header
        try:
            self.sheet_df = pd.read_excel(self.input_file, 'Biological Material')
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
                    "CHECK FAILED - The Biological Material sheet has a invalid format (some fields are incorrectly formatted).")
                self.run = False
                #sys.exit(" - ERROR - Invalid Field Formats in Biological Material Sheet - ")

        except ValueError:
            self.logs.append("CHECK FAILED - The Biological Material sheet cannot be opened.")
            self.run = False

    #  -  Check Environment Sheet  -

    def CheckEnvironmentSheet(self):
        # Check Environment Sheet Header
        # No format checking in this sheet (maybe implement, maybe not)
        try:
            self.sheet_df = pd.read_excel(self.input_file, 'Environment')
            # Remove '*' characters, which indicate mandatory columns to fill
            environment_header = [ele.replace('*', '') for ele in list(self.sheet_df)]

            # Valid Environment sheet Headers:
            valid_environment_header1 = ["Environment parameter", "Environment parameter value"]
            valid_environment_header2 = ["Study unique ID", "Environment parameter", "Environment parameter value"]

            if environment_header == valid_environment_header1 or environment_header == valid_environment_header2:
                self.logs.append("CHECK PASSED - The Environment sheet has a valid header (column name/number).")
            else:
                self.logs.append("CHECK FAILED - The Environment sheet has an invalid header (column name/number).")
                self.run = False
                #sys.exit(" - ERROR - Invalid Header in Environment Sheet - ")

        except ValueError:
            self.logs.append("CHECK FAILED - The Environment sheet cannot be opened.")
            self.run = False

    #  -  Check Environment Factor Sheet  -

    def CheckExperimentalFactorSheet(self):
        # Check Experimental Factor Sheet Header (In MIAPPE specs it's named Environment Factor)
        # No format checking in this sheet (maybe implement, maybe not)
        try:
            self.sheet_df = pd.read_excel(self.input_file, 'Factor')
            # Remove '*' characters, which indicate mandatory columns to fill
            expfactor_header = [ele.replace('*', '') for ele in list(self.sheet_df)]

            # Valid Experimental Factor sheet Headers:
            valid_expfactor_header1 = ["Experimental parameter", "Experimental parameter value"]
            valid_expfactor_header2 = ["Study unique ID", "Factor type", "Factor description", "Factor values"]

            if expfactor_header == valid_expfactor_header1 or expfactor_header == valid_expfactor_header2:
                self.logs.append("CHECK PASSED - The Experimental Factor sheet has a valid header (column name/number).")
            else:
                self.logs.append("CHECK FAILED - The Experimental Factor sheet has an invalid header (column name/number).")
                self.run = False
                #sys.exit(" - ERROR - Invalid Header in Experimental Factor Sheet - ")

        except ValueError:
            self.logs.append("CHECK FAILED - The Experimental Factor sheet cannot be opened.")
            self.run = False


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


    #  -  Check Observation Unit Sheet  -

    def CheckObservationUnitSheet(self):
        # Check Observation Unit Sheet Header (In MIAPPE specs it's named Environment Factor)
        try:
            self.sheet_df = pd.read_excel(self.input_file, 'Observation Unit')
            # Remove '*' characters, which indicate mandatory columns to fill
            obsunit_header = [ele.replace('*', '') for ele in list(self.sheet_df)]

            # Valid Observation Unit sheet Headers:
            valid_obsunit_header1 = ["Observation unit ID", "Observation unit type", "External ID", "Spatial distribution",
                                    "Observation Unit factor value"]
            valid_obsunit_header2 = ["Study unique ID", "Biological Material ID", "Observation unit ID",
                                    "Observation unit type", "External ID", "Spatial distribution",
                                    "Observation unit factor value"]

            if obsunit_header == valid_obsunit_header1 or obsunit_header == valid_obsunit_header2:
                self.logs.append("CHECK PASSED - The Observation Unit sheet has a valid header (column name/number).")
            else:
                self.logs.append("CHECK FAILED - The Observation Unit sheet has an invalid header (column name/number).")
                self.run = False
                #sys.exit(" - ERROR - Invalid Header in Observation Unit Sheet - ")

        except ValueError:
            self.logs.append("CHECK FAILED - The Observation Unit sheet cannot be opened.")
            self.run = False


    #  -  Check Sample Sheet  -

    def CheckSampleSheet(self):
        # Check Sample Sheet Header
        try:
            self.sheet_df = pd.read_excel(self.input_file, 'Sample')
            # Remove '*' characters, which indicate mandatory columns to fill
            sample_header = [ele.replace('*', '') for ele in list(self.sheet_df)]

            # Valid Sample sheet Headers:
            valid_sample_header1 = ["Sample ID", "Plant structure development stage", "Plant anatomical entity",
                                    "Sample description", "Collection date", "External ID"]
            valid_sample_header2 = ["Observation unit ID", "Sample ID", "Plant structure development stage",
                                    "Plant anatomical entity", "Sample description", "Collection date", "External ID"]

            if sample_header == valid_sample_header1 or sample_header == valid_sample_header2:
                self.logs.append("CHECK PASSED - The Sample sheet has a valid header (column name/number).")
            else:
                self.logs.append("CHECK FAILED - The Sample sheet has an invalid header (column name/number).")
                self.run = False
                #sys.exit(" - ERROR - Invalid Header in Sample Sheet - ")

        except ValueError:
            self.logs.append("CHECK FAILED - The Sample sheet cannot be opened.")
            self.run = False


    #  -  Check Observed Variable Sheet  -

    def CheckObservedVariableSheet(self):
        # Check Observed Variable Sheet Header
        try:
            self.sheet_df = pd.read_excel(self.input_file, 'Observed Variable')
            # Remove '*' characters, which indicate mandatory columns to fill
            obsvariable_header = [ele.replace('*', '') for ele in list(self.sheet_df)]

            # Valid Observed Variable sheet Headers:
            valid_obsvariable_header1 = ["Variable ID", "Variable name", "Variable accession number", "Trait",
                                        "Trait accession number", "Method", "Method accession number", "Method description",
                                        "Reference associated to the method", "Scale", "Scale accession number", "Time scale"]
            valid_obsvariable_header2 = ["Study unique ID", "Variable ID", "Variable name", "Variable accession number",
                                        "Trait", "Trait accession number", "Method", "Method accession number",
                                        "Method description", "Reference associated to the method", "Scale",
                                        "Scale accession number", "Time scale"]

            if obsvariable_header == valid_obsvariable_header1 or obsvariable_header == valid_obsvariable_header2:
                self.logs.append("CHECK PASSED - The Observed Variable sheet has a valid header (column name/number).")
            else:
                self.logs.append("CHECK FAILED - The Observed Variable sheet has an invalid header (column name/number).")
                self.run = False
                #sys.exit(" - ERROR - Invalid Header in Observed Variable Sheet - ")

        except ValueError:
            self.logs.append("CHECK FAILED - The Observed Variable sheet cannot be opened.")
            self.run = False




    #       ----------        MAIN CODE        ----------

    # Input File (read from above_script.js)

    # input_file = 'Rice_Miappe_Test_v2.xlsx'
    #input_file = sys.argv[1]

    # The input file should end in .xlsx, .xls or .ods
    # Additional excel-like files which may be considered (older versions): .xlsm; .xlsb; .xml; .xltx; .xlt; .xltm; .xlam; .xlc; xld; .xlk; .xlw; .xlr.

    def run_miappe_validator(self):

        if self.run == True:
            self.check_input_file()
        if self.run == True:
            self.CheckInvestigationSheet()
        if self.run == True:
            self.CheckStudySheet()
        if self.run == True:
            self.CheckPersonSheet()
        if self.run == True:
            self.CheckDatafileSheet()
        if self.run == True:
            self.CheckBiologicalMaterialSheet()
        if self.run == True:
            self.CheckEnvironmentSheet()
        if self.run == True:
            self.CheckExperimentalFactorSheet()
        if self.run == True:
            self.CheckEventSheet()
        if self.run == True:
            self.CheckObservationUnitSheet()
        if self.run == True:
            self.CheckSampleSheet()
        if self.run == True:
            self.CheckObservedVariableSheet()

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

