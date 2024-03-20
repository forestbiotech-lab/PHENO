# Miappe validation script v0.1

First version for checking sheet names, columns and formats in input Excel files in OntoBrAPI.


#### Validator 

The validator runs in a docker based on a python image, to ensure no issues with dependency on server. The webserver file allows communication between containers via networking. The webserver imports the miappe_validator.py and runs it with the POST request file in the file attribute of the POST request. The webserver will listen on port 8080 and the and compose will redirect that to port 3004 on the local machine. The container also mount bind the upload directory for convinence of access. This way on upload of the file it can access the new file. 

The struture of the validator is a series of methods that progressively check the file. However only the 2 first have been verified. The previous execution exit would not be viable as it would kill the webserver. Suggestion is to define a can continue parameter in self that is checked in all the validation methods. 


To test the server with the following file: 
```bash
 curl -X POST "localhost:3004" -H 'Content-Type: application/json' -d '{"file":"external/Vitis_MiappeV1.1.xlsx"}'
```
The python webserver has the uplod/uploaded_files directory mounted as external so you can refere to any file in the uploaded_files for testing purposes.
 

## Open documents format dependencies

The [ODFPy](https://pypi.org/project/odfpy/) driver initially used to read *.ods* files is extremly slow. As an alternative the [pyexcel-ods3](https://github.com/pyexcel/pyexcel-ods3) driver as be adapted, to use in case the uploaded data is a *.ods* file. However, this isn't implementing the dataformat validation on these files. As an alternative which uses partial loading of *.ods*, the driver [pyexcel-odsr](https://github.com/pyexcel/pyexcel-odsr) can be use in future iterations. 
