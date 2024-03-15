# Welcome to OntoBrAPI
![OntoBrAPI logo](https://github.com/forestbiotech-lab/ontoBrAPI-node-docker/blob/master/public/images/logo.png)

# Index
- [What is OntoBrAPI?](README.md#what-is-ontobrapi-1)
- [How to setup OntoBrAPI locally?](README.md#how-to-setup-ontobrapi-locally-1)
- [SparQL](README.md#sparql)
- [Instance requirements](README.md#instance-requirements)


# What is OntoBrAPI?
OntoBrAPI has 3 main functions based on international standards:
- Data submission (MIAPPE)
- Data storage (RDF)
- Data sharing (BrAPI)

### 1) Data submission
OntoBrAPI runs on a web server, which provides a Graphical User Interface (GUI) that allows the conversion of the MIAPPE spreadsheet into n-triples format. The GUI allows the user to dynamically map the MIAPPE spreadsheet to the appropriate PPEO ontological properties using a JavaScript Object Notation (JSON). The user can also start from an initial mapping in JSON and adjust any fields deemed necessary. The GUI uses the constraints coded in the ontology to validate the mapping. As an example the data types allowed for each of the data properties is enforced by the GUI, which are inherited from the rules in the ontology; the same goes for the object properties that can link classes and the data properties that can annotate the classes.

### 2) Data Storage 
OntoBrAPI relies on [OpenLink Virtuoso](https://docs.openlinksw.com/virtuoso/) to store triples and builds a management system for data curators to validate datasets and select which datasets are ready for sharing.

### 3) Data Sharing
OntoBrAPI provides a BrAPI endpoint which delivers data in the triple store as JSON. This module allows administratores to update the data properties mapped to the respective JSON output in acordance with the [BrAPI specification](https://brapi.org/specification). 






# How to setup OntoBrAPI locally?

Since OntoBrAPI relies on several external components, it's designed as a collection of individual Docker containers. This approach, facilitated by [Docker Compose](https://docs.docker.com/compose/), simplifies the setup process.


## Setup your environment (Running on compose)
You can use your computer or an instance on a Virtual Private Cloud (VPC) provider (ex: AWS, Azure, Google Cloud,etc). 
The dependencies will be installed by running this script on a Ubuntu system. 

#### Dependencies are:
- [git](https://git-scm.com/)
- [docker](https://www.docker.com/)
- [compose](https://docs.docker.com/compose/)
  
```
wget https://github.com/forestbiotech-lab/ontoBrAPI/raw/master/setup.sh -o setup.sh
bash setup.sh 
```

## Setup a development environment
This solution is the best if you want to debug a particular module and deal with the dependencies directly. Most containers are based on node will others are python. Refere to the docker file to check the appropriate setup of each module. To get the files on your setup use git.

Clone repo and init Submodules, replace repository url based on the access to the project. git@github.com...... or https://github.com.......

**For collaboratores use this**:
``` bash
git clone git@github.com:forestbiotech-lab/ontoBrAPI.git
cd ontoBrapi
git submodule init
git submodule update
git checkout master
``` 
**For other users try this**:
``` bash
git clone http://github.com/forestbiotech-lab/ontoBrAPI.git
cd ontoBrapi
git submodule init

#git submodule set-url [repo] [repo-url]
#Do this for every repo in submodules
git submodule set-url ontoBrAPI-node-docker  https://github.com/forestbiotech-lab/ontoBrAPI-node-docker.git
git submodule set-url ontobrapi-admin  https://github.com/forestbiotech-lab/ontobrapi-admin.git
git submodule set-url ontobrapi-brapi  https://github.com/forestbiotech-lab/ontobrapi-brapi.git
git submodule update
cd ontoBrAPI-node-docker
git checkout master
cd ../ontobrapi-admin
git checkout main
cd ../ontobrapi-brapi
git checkout master
cd ..
``` 

Build / Rebuild web module container (First run)
``` bash
docker-compose up -d --build
```
or just to spin up the containers

``` bash
docker-compose up -d
```

### Node modules
For node modules you must have [NodeJs](https://nodejs.org) installed and use npm to start the web server, check the dockerfile for help on all the dependencies. 
```
#Port should be one that does not colide with the currently active ports on the setup
PORT=3010 npm start
```

# SparQL
This sections describes basic usage of SparQL, but please refere to the [Wiki page](https://github.com/forestbiotech-lab/ontoBrAPI/wiki/SparQL) for more details. The SparQL query editor is accessible on port 8890 (ex: localhost:8890/sparql) and is referenced in docker-compose as DB. Currently, SparQL queries are executed by [OpenLink Virtuoso](https://docs.openlinksw.com/virtuoso/). 

Default user and password are: **dba** 

## From docker image:
- The Virtuoso password can be set at container start up via the DBA_PASSWORD environment variable. If not set, the default dba password will be used.

### SPARQL update permission
The SPARQL_UPDATE permission on the SPARQL endpoint can be granted by setting the SPARQL_UPDATE environment variable to true.

### .ini configuration
All properties defined in virtuoso.ini can be configured via the environment variables. The environment variable should be prefixed with VIRT_ and have a format like VIRT_$SECTION_$KEY. $SECTION and $KEY are case sensitive. They should be CamelCased as in virtuoso.ini. E.g. property ErrorLogFile in the Database section should be configured as VIRT_Database_ErrorLogFile=error.log.




# Instance requirements

The validation takes some time on small instances because of the 

|  Image  |  RAM |   Disk space |
----------|-------|---------|
DB        | 300M |    0.27Gb 
Mongo     | 120M |   0.70Gb
Admin     |  42M |   1.90Gb
gateway   |   3M |   0.19Gb
validator |  25M |   1.31Gb
web       |  25M |   1.03Gb
brapi     |   ?M |
**TOTAL**   | **~520M**|   **~6.00Gb**  

~
+ 0.9Gb Node



HD 16GB 
