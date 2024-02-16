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
        self.logs = ["   --- OntoBrAPI - Input File Validity Report ---   "]
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

        if set(self.sheetsList) <= set(valid_sheet_names):
            if len(self.sheetsList) == 11:
                self.logs.append(
                    "CHECK PASSED - The " + str(len(self.sheetsList)) + " sheet names of the excel input file are valid.")
            else:
                self.logs.append("CHECK WARNING - The input file does not have 11 sheets.")
        else:
            self.logs.append("CHECK FAILED - The input file contains invalid sheet names.")
            self.run = False


    #  -  Check Investigation Sheet  -

    def CheckInvestigationSheet(self):
        # Check Investigation Sheet Header
        try:
            self.sheet_df = pd.read_excel(self.input_file, 'Investigation')
            # Remove '*' characters, which indicate mandatory columns to fill
            investigation_header = [ele.replace('*', '') for ele in list(self.sheet_df)]

            valid_investigation_header = ["Investigation unique ID", "Investigation title", "Investigation description",
                                          "Submission date", "Public release date", "License", "MIAPPE version",
                                          "Associated publication"]

            if investigation_header == valid_investigation_header:
                self.logs.append("CHECK PASSED - The Investigation sheet has a valid header (column name/number).")
            else:
                self.logs.append("CHECK FAILED - The Investigation sheet has an invalid header (column name/number).")
                self.run = False

            # Cleaning "\n" characters from the dataframe
            self.sheet_df.replace({'\n': ''}, regex=True)

            # Check Investigation field formats per column
            investigation_format = self.sheet_df.dtypes

            valid_investigation_format = "[dtype('O'), dtype('O'), dtype('O'), dtype('<M8[ns]'), dtype('<M8[ns]'), dtype('O'), dtype('float64'), dtype('float64')]"

            if str(list(investigation_format)) == valid_investigation_format:
                self.logs.append(
                    "CHECK PASSED - The Investigation sheet has a valid format (properly formated fields).")
            else:
                self.logs.append(
                    "CHECK FAILED - The Investigation sheet has a invalid format (some fields are incorrectly formated).")
                self.run = False

            # Check if the Investigation unique ID holds unique values

            investigation_unid_col = self.sheet_df.loc[:, "Investigation unique ID"].is_unique
            if investigation_unid_col == True:
                self.logs.append("CHECK PASSED - The Investigation sheet has no duplicate Investigation unique IDs.")
            else:
                self.logs.append(
                    "CHECK FAILED - The Investigation sheet has duplicate Investigation unique IDs (they should be unique).")
                self.run = False


        except ValueError:
            self.logs.append("CHECK FAILED - The Investigation sheet cannot be opened.")
            self.run = False


    #  -  Check Study Sheet  -

    def CheckStudySheet(self):
        # Check Study Sheet Header
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

        if study_header == valid_study_header1 or study_header == valid_study_header2:
            self.logs.append("CHECK PASSED - The Study sheet has a valid header (column name/number).")
        else:
            self.logs.append("CHECK FAILED - The Study sheet has an invalid header (column name/number).")
            self.run = False


    #  -  Check Person Sheet  -

    def CheckPersonSheet(input_file, logs):
        # Check Person Sheet Header
        sheet_df = pd.read_excel(input_file, 'Person')
        # Remove '*' characters, which indicate mandatory columns to fill
        person_header = [ele.replace('*', '') for ele in list(sheet_df)]

        # Valid Person sheet Headers:
        valid_person_header1 = ["Person name", "Person email", "Person ID", "Person role", "Person affiliation"]
        valid_person_header2 = ["Study unique ID", "Person name", "Person email", "Person ID", "Person role",
                                "Person affiliation"]

        if person_header == valid_person_header1 or person_header == valid_person_header2:
            logs.append("CHECK PASSED - The Person sheet has a valid header (column name/number).")
        else:
            logs.append("CHECK FAILED - The Person sheet has an invalid header (column name/number).")
            #sys.exit(" - ERROR - Invalid Header in Person Sheet - ")

        # Cleaning "\n" characters from the dataframe
        sheet_df.replace({'\n': ''}, regex=True)

        # Check Person field formats per column
        person_format = sheet_df.dtypes

        valid_person_format = "[dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('O')]"

        if str(list(person_format)) == valid_person_format:
            logs.append("CHECK PASSED - The Person sheet has a valid format (properly formated fields).")
        else:
            logs.append("CHECK FAILED - The Person sheet has a invalid format (some fields are incorrectly formated).")
            #sys.exit(" - ERROR - Invalid Field Formats in Person Sheet - ")


    #  -  Check Data File Sheet  -

    def CheckDatafileSheet(input_file, logs):
        # Check Data File Sheet Header (In MIAPPE specs it is named Data File)
        sheet_df = pd.read_excel(input_file, 'Data file')
        # Remove '*' characters, which indicate mandatory columns to fill
        datafile_header = [ele.replace('*', '') for ele in list(sheet_df)]

        # Valid Data File sheet Headers:
        valid_datafile_header1 = ["Data file link", "Data file description", "Data file version"]
        valid_datafile_header2 = ["Study unique ID", "Data file link", "Data file description", "Data file version"]

        if datafile_header == valid_datafile_header1 or datafile_header == valid_datafile_header2:
            logs.append("CHECK PASSED - The Data File sheet has a valid header (column name/number).")
        else:
            logs.append("CHECK FAILED - The Data File sheet has an invalid header (column name/number).")
            #sys.exit(" - ERROR - Invalid Header in Data File Sheet - ")

        # Cleaning "\n" characters from the dataframe
        sheet_df.replace({'\n': ''}, regex=True)

        # Check Data Field field formats per column
        datafile_format = sheet_df.dtypes

        valid_datafile_format = "[dtype('O'), dtype('O'), dtype('O'), dtype('O')]"

        if str(list(datafile_format)) == valid_datafile_format:
            logs.append("CHECK PASSED - The Data File sheet has a valid format (properly formated fields).")
        else:
            logs.append("CHECK FAILED - The Data File sheet has a invalid format (some fields are incorrectly formated).")
            #sys.exit(" - ERROR - Invalid Field Formats in Data File Sheet - ")


    #  -  Check Biological Material Sheet  -

    def CheckBiologicalMaterialSheet(input_file, logs):
        # Check Biological Material Sheet Header
        sheet_df = pd.read_excel(input_file, 'Biological Material')
        # Remove '*' characters, which indicate mandatory columns to fill
        biomaterial_header = [ele.replace('*', '') for ele in list(sheet_df)]

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
            logs.append("CHECK PASSED - The Biological Material sheet has a valid header (column name/number).")
        else:
            logs.append("CHECK FAILED - The Biological Material sheet has an invalid header (column name/number).")
            #sys.exit(" - ERROR - Invalid Header in Biological Material Sheet - ")

        # Cleaning "\n" characters from the dataframe
        sheet_df.replace({'\n': ''}, regex=True)

        # Check Biological Material field formats per column
        biomaterial_format = sheet_df.dtypes

        valid_biomaterial_format = "[dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('float64'), dtype('float64'), dtype('O'), dtype('float64'), dtype('float64'), dtype('O'), dtype('O'), dtype('float64'), dtype('float64'), dtype('float64'), dtype('float64'), dtype('O')]"

        if str(list(biomaterial_format)) == valid_biomaterial_format:
            logs.append("CHECK PASSED - The Biological Material sheet has a valid format (properly formated fields).")
        else:
            logs.append(
                "CHECK FAILED - The Biological Material sheet has a invalid format (some fields are incorrectly formated).")
            #sys.exit(" - ERROR - Invalid Field Formats in Biological Material Sheet - ")


    #  -  Check Environment Sheet  -

    def CheckEnvironmentSheet(input_file, logs):
        # Check Environment Sheet Header
        sheet_df = pd.read_excel(input_file, 'Environment')
        # Remove '*' characters, which indicate mandatory columns to fill
        environment_header = [ele.replace('*', '') for ele in list(sheet_df)]

        # Valid Environment sheet Headers:
        valid_environment_header1 = ["Environment parameter", "Environment parameter value"]
        valid_environment_header2 = ["Study unique ID", "Environment parameter", "Environment parameter value"]

        if environment_header == valid_environment_header1 or environment_header == valid_environment_header2:
            logs.append("CHECK PASSED - The Environment sheet has a valid header (column name/number).")
        else:
            logs.append("CHECK FAILED - The Environment sheet has an invalid header (column name/number).")
            #sys.exit(" - ERROR - Invalid Header in Environment Sheet - ")


    #  -  Check Environment Factor Sheet  -

    def CheckExperimentalFactorSheet(input_file, logs):
        # Check Experimental Factor Sheet Header (In MIAPPE specs it's named Environment Factor)
        sheet_df = pd.read_excel(input_file, 'Factor')
        # Remove '*' characters, which indicate mandatory columns to fill
        expfactor_header = [ele.replace('*', '') for ele in list(sheet_df)]

        # Valid Experimental Factor sheet Headers:
        valid_expfactor_header1 = ["Experimental parameter", "Experimental parameter value"]
        valid_expfactor_header2 = ["Study unique ID", "Factor type", "Factor description", "Factor values"]

        if expfactor_header == valid_expfactor_header1 or expfactor_header == valid_expfactor_header2:
            logs.append("CHECK PASSED - The Experimental Factor sheet has a valid header (column name/number).")
        else:
            logs.append("CHECK FAILED - The Experimental Factor sheet has an invalid header (column name/number).")
            #sys.exit(" - ERROR - Invalid Header in Experimental Factor Sheet - ")


    #  -  Check Event Sheet  -

    def CheckEventSheet(input_file, logs):
        # Check Event Sheet Header
        sheet_df = pd.read_excel(input_file, 'Event')
        # Remove '*' characters, which indicate mandatory columns to fill
        event_header = [ele.replace('*', '') for ele in list(sheet_df)]

        # Valid Event sheet Headers:
        valid_event_header1 = ["Event type", "Event accession number", "Event description", "Event date"]
        valid_event_header2 = ["Study unique ID", "Observation unit ID", "Event type", "Event acession number",
                               "Event description", "Event date"]
        # Custom MIAPPE (header2) misspells "accession" with "acession"

        if event_header == valid_event_header1 or event_header == valid_event_header2:
            logs.append("CHECK PASSED - The Event sheet has a valid header (column name/number).")
        else:
            logs.append("CHECK FAILED - The Event sheet has an invalid header (column name/number).")
            #sys.exit(" - ERROR - Invalid Header in Event Sheet - ")

        # Cleaning "\n" characters from the dataframe
        sheet_df.replace({'\n': ''}, regex=True)

        # Check Event field formats per column
        event_format = sheet_df.dtypes

        # Skip format validation if this sheet is empty
        if len(sheet_df.index) != 0:
            valid_event_format = "[dtype('O'), dtype('O'), dtype('O'), dtype('<M8[ns]')]"

            if str(list(event_format)) == valid_event_format:
                logs.append("CHECK PASSED - The Event sheet has a valid format (properly formated fields).")
            else:
                logs.append("CHECK FAILED - The Event sheet has a invalid format (some fields are incorrectly formated).")
                #sys.exit(" - ERROR - Invalid Field Formats in Event Sheet - ")
        else:
            logs.append("CHECK WARNING - The Event sheet is empty (no format check applied).")


    #  -  Check Observation Unit Sheet  -

    def CheckObservationUnitSheet(input_file, logs):
        # Check Observation Unit Sheet Header (In MIAPPE specs it's named Environment Factor)
        sheet_df = pd.read_excel(input_file, 'Observation Unit')
        # Remove '*' characters, which indicate mandatory columns to fill
        obsunit_header = [ele.replace('*', '') for ele in list(sheet_df)]

        # Valid Observation Unit sheet Headers:
        valid_obsunit_header1 = ["Observation unit ID", "Observation unit type", "External ID", "Spatial distribution",
                                 "Observation Unit factor value"]
        valid_obsunit_header2 = ["Study unique ID", "Biological Material ID", "Observation unit ID",
                                 "Observation unit type", "External ID", "Spatial distribution",
                                 "Observation unit factor value"]

        if obsunit_header == valid_obsunit_header1 or obsunit_header == valid_obsunit_header2:
            logs.append("CHECK PASSED - The Observation Unit sheet has a valid header (column name/number).")
        else:
            logs.append("CHECK FAILED - The Observation Unit sheet has an invalid header (column name/number).")
            #sys.exit(" - ERROR - Invalid Header in Observation Unit Sheet - ")


    #  -  Check Sample Sheet  -

    def CheckSampleSheet(input_file, logs):
        # Check Sample Sheet Header
        sheet_df = pd.read_excel(input_file, 'Sample')
        # Remove '*' characters, which indicate mandatory columns to fill
        sample_header = [ele.replace('*', '') for ele in list(sheet_df)]

        # Valid Sample sheet Headers:
        valid_sample_header1 = ["Sample ID", "Plant structure development stage", "Plant anatomical entity",
                                "Sample description", "Collection date", "External ID"]
        valid_sample_header2 = ["Observation unit ID", "Sample ID", "Plant structure development stage",
                                "Plant anatomical entity", "Sample description", "Collection date", "External ID"]

        if sample_header == valid_sample_header1 or sample_header == valid_sample_header2:
            logs.append("CHECK PASSED - The Sample sheet has a valid header (column name/number).")
        else:
            logs.append("CHECK FAILED - The Sample sheet has an invalid header (column name/number).")
            #sys.exit(" - ERROR - Invalid Header in Sample Sheet - ")


    #  -  Check Observed Variable Sheet  -

    def CheckObservedVariableSheet(input_file, logs):
        # Check Observed Variable Sheet Header
        sheet_df = pd.read_excel(input_file, 'Observed Variable')
        # Remove '*' characters, which indicate mandatory columns to fill
        obsvariable_header = [ele.replace('*', '') for ele in list(sheet_df)]

        # Valid Observed Variable sheet Headers:
        valid_obsvariable_header1 = ["Variable ID", "Variable name", "Variable accession number", "Trait",
                                     "Trait accession number", "Method", "Method accession number", "Method description",
                                     "Reference associated to the method", "Scale", "Scale accession number", "Time scale"]
        valid_obsvariable_header2 = ["Study unique ID", "Variable ID", "Variable name", "Variable accession number",
                                     "Trait", "Trait accession number", "Method", "Method accession number",
                                     "Method description", "Reference associated to the method", "Scale",
                                     "Scale accession number", "Time scale"]

        if obsvariable_header == valid_obsvariable_header1 or obsvariable_header == valid_obsvariable_header2:
            logs.append("CHECK PASSED - The Observed Variable sheet has a valid header (column name/number).")
        else:
            logs.append("CHECK FAILED - The Observed Variable sheet has an invalid header (column name/number).")
            #sys.exit(" - ERROR - Invalid Header in Observed Variable Sheet - ")




    #       ----------        MAIN CODE        ----------

    # Write validation report to a logs list, write to .log file at the end


    # Input File (read from above_script.js)

    # input_file = 'Rice_Miappe_Test_v2.xlsx'
    #input_file = sys.argv[1]

    # The input file should end in .xlsx or .xls for older versions.
    # Additional excel-like files which may be considered: .xlsm; .xlsb; .xml; .xltx; .xlt; .xltm; .xlam; .xlc; xld; .xlk; .xlw; .xlr.

    def run_miappe_validator(self):

        if self.run == True:
            self.check_input_file()
        if self.run == True:
            self.CheckInvestigationSheet()
        if self.run == True:
            self.CheckStudySheet()
        #CheckPersonSheet()
        #CheckDatafileSheet()
        #CheckBiologicalMaterialSheet()
        #CheckEnvironmentSheet()
        #CheckExperimentalFactorSheet()
        #CheckEventSheet()
        #CheckObservationUnitSheet(input_file, logs)
        #CheckSampleSheet(input_file, logs)

        # Write miappe_validator_logs file:
        # Append File is Valid if self.run reaches the end as True
        if self.run == True:
            self.logs.append(" - THE INPUT FILE IS VALID - ")

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

