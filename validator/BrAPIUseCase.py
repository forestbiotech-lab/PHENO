import json
import requests
import pandas as pd
from pyDataverse.api import NativeApi, DataAccessApi
from pyDataverse.models import Dataverse
from urllib.parse import urlparse
from urllib.parse import parse_qs


def list_data_verse_files(url):
    o = urlparse(url)
    base_url = o.scheme + "://" + o.hostname
    api = NativeApi(base_url)
    data_api = DataAccessApi(base_url)
    DOI = parse_qs(o.query)['persistentId'][0]
    dataset = api.get_dataset(DOI)
    files_list = dataset.json()['data']['latestVersion']['files']
    print(files_list)


def get_data_verse_files(url, idx):
    o = urlparse(url)
    base_url = o.scheme + "://" + o.hostname
    api = NativeApi(base_url)
    data_api = DataAccessApi(base_url)
    doi = parse_qs(o.query)['persistentId'][0]
    dataset = api.get_dataset(doi)
    files_list = dataset.json()['data']['latestVersion']['files']
    file_id = files_list[idx]['dataFile']['id']
    return data_api.get_datafile(file_id)


def list_studies(data):
    for idx, study in enumerate(data['result']['data']):
        #filter for traceRice studies
        print(f'trialName{idx}: ', study['trialName'])
        print(f'studyName{idx}:', study['studyName'])
        print(f'culturalPractices{idx}:', study['culturalPractices'])
        print(f'dataLinks{idx}: ', study['dataLinks'])

def list_observed_variables(data):
    for idx, obsVar in enumerate(data['result']['data']):
        print(f'observationVariableDbId{idx}: ', obsVar['observationVariableDbId'])
        print(f'observationVariableName{idx}:', obsVar['observationVariableName'])
        print(f'method.description{idx}: ', obsVar['method']['description'])


def get_study_data_link(data, idx):
    return data['result']['data'][idx]['dataLinks']


def get_observation_variable(data, idx):
    return data['result']['data'][idx]['observationVariableDbId']


def get_brapi_data(call, page, page_size):
    url = host + calls[call]
    response = requests.get(f'{url}?page={page}&pageSize={page_size}')
    if response.status_code == 200:
        brAPI_data = json.loads(response.text)
        return brAPI_data
    else:
        return None


def load_data(study_datalink_url,idx):
    file = get_data_verse_files(study_datalink_url, idx)
    return pd.read_csv(file.url, sep="\t")


host = "http://localhost:3003"
calls = {'study': "/admin/brapi/listCalls/core/study.json/result",
         "observationVariables": "/admin/brapi/listcalls/phenotyping/observationVariables.json/result"}

study_data = get_brapi_data("study", 0, 2)
list_studies(study_data)
study_datalink = get_study_data_link(study_data, 1)
study_datalink_url = study_datalink[0]["url"]
list_data_verse_files(study_datalink_url)
data_file = load_data(study_datalink_url, 0)
df = data_file

#names of rows and columns
df.columns = df.iloc[1]
df.index = df['Rice variety']

#Cut dataframe
df = df.iloc[:46, :17]
print(df)

observed_variables_data = get_brapi_data("observationVariables", 1, 3)
list_observed_variables(observed_variables_data)

obsVar0 = get_observation_variable(observed_variables_data, 0)
obsVar1 = get_observation_variable(observed_variables_data, 1)
obsVar2 = get_observation_variable(observed_variables_data, 2)

values = df.loc[df.index == 'Bomba ', [obsVar0, obsVar1, obsVar2]].astype('float')
means = df.loc[df.index == 'Bomba ', [obsVar0, obsVar1, obsVar2]].astype('float').mean()

print(values)
print(means)
















