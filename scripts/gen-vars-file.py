from conflog import Conflog
from modrinth_api_wrapper import Client
import yaml

cfl = Conflog(conf_files=['./config/conflog.yaml'])
logger = cfl.get_logger('gen-vars-file')

def retrieve_fabric_api_versions_data():
    logger.info('Retrieving Fabric API versions data...')

    data = {
        'fabric_api_versions': {}
    }

    modrinth_client = Client()

    for version_id in modrinth_client.get_project(project_id="fabric-api").versions:
        version = modrinth_client.get_version(version_id=version_id)

        data['fabric_api_versions'][version.version_number] = {
            'sha1': version.files[0].hashes.sha1,
            'url': version.files[0].url
        }

    logger.info('Fabric API versions data retrieved successfully')
    return data

def write_vars_file(data, file_path):
    logger.info(f'Writing vars file at {file_path} ...')
    vars_data_in_yaml = yaml.safe_dump(data, explicit_start=True)
    with open(file_path, 'w') as file:
        file.write(vars_data_in_yaml)
        logger.info('Vars file written successfully')

fabric_api_data = retrieve_fabric_api_versions_data()
write_vars_file(fabric_api_data, 'vars/main.yml')