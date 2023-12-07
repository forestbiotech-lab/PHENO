
const spawner = require('child_process').spawn;

// string
const data_to_pass_in = '../ontoBrAPI-node-docker/reference_files/valores de Cópia de MIAPPEv1.1_compliant_vitis_submissionOntobrapi.ods';

console.log('Data sent to python script:', data_to_pass_in);

const pythonProcess = spawner('python3', ['./miappe_validator.py', data_to_pass_in]);

pythonProcess.stdout.on('data', (data) => {
    console.log('Data received from python script:', data.toString());
});

pythonProcess.stderr.on('data', (data) => {
    console.log('Data received from python script:', data.toString());
});
