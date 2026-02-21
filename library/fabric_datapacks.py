#!/usr/bin/python

DOCUMENTATION = r'''
---
module: fabric_datapacks
short_description: Install Fabric datapacks
requirements:
  - conflog
  - modrinth-api-wrapper
  - requests
'''

from conflog import Conflog
from ansible.module_utils.basic import AnsibleModule
from modrinth_api_wrapper import Client
import os
import requests
import time

conf_dict={
    'handlers': 'stream',
    'datefmt': "%Y%m%d%H%M%S",
    'format': "[fabric-datapacks] [%(levelname)s] [%(asctime)s] %(message)s",
    'level': "debug"
}
cfl = Conflog(conf_dict=conf_dict)
logger = cfl.get_logger('fabric_datapacks')


def download_datapack(client, datapack_slug, game_version, dest_dir):
    """Download a datapack from Modrinth.

    Returns True if a datapack was downloaded, False if it already existed.
    """
    logger.info(f"Fetching project versions for '{datapack_slug}'...")

    versions = client.list_project_versions(datapack_slug)

    compatible_versions = [
        v for v in versions
        if game_version in v.game_versions
    ]

    if not compatible_versions:
        raise Exception(
            f"No compatible version found for datapack '{datapack_slug}' with Minecraft {game_version}"
        )

    version = compatible_versions[0]

    primary_file = None
    for file in version.files:
        if file.primary and file.filename.lower().endswith('.zip'):
            primary_file = file
            break

    if not primary_file:
        for file in version.files:
            if file.filename.lower().endswith('.zip'):
                primary_file = file
                break

    if not primary_file:
        raise Exception(f"No downloadable zip file found for datapack '{datapack_slug}'")

    download_url = primary_file.url
    filename = primary_file.filename
    dest_path = os.path.join(dest_dir, filename)

    if os.path.exists(dest_path):
        logger.info(f"Datapack '{filename}' already exists at '{dest_path}', skipping download")
        return False

    logger.info(f"Downloading '{filename}' from {download_url}...")
    response = requests.get(download_url, stream=True)
    response.raise_for_status()

    with open(dest_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    logger.info(f"Successfully downloaded '{filename}' to '{dest_path}'")
    return True


def main():

    module_args = dict(
        minecraft_version=dict(type="str", required=True),
        datapacks=dict(type="list", elements="str", required=True),
        datapacks_download_delay=dict(type="int", required=True),
        world=dict(type="str", required=True),
        install_dir=dict(type="str", required=True),
    )
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    minecraft_version = module.params["minecraft_version"]
    datapacks = module.params["datapacks"]
    datapacks_download_delay = module.params["datapacks_download_delay"]
    world = module.params["world"]
    install_dir = module.params["install_dir"]

    logger.info(
        f"'{len(datapacks)}' Fabric datapack(s) to be installed for world '{world}' and Minecraft version '{minecraft_version}'..."
    )

    client = Client()
    datapacks_dir = os.path.join(install_dir, "workspace", world, "datapacks")
    os.makedirs(datapacks_dir, exist_ok=True)

    changed = False
    for datapack in datapacks:
        logger.info(f"Installing Fabric datapack '{datapack}' for world '{world}'...")
        if download_datapack(client, datapack, minecraft_version, datapacks_dir):
            changed = True
        time.sleep(datapacks_download_delay)

    result = {
        "changed": changed,
    }
    module.exit_json(**result)


if __name__ == "__main__":
    main()
