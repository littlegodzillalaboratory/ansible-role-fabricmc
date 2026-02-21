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
import hashlib
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


def get_expected_hash(file_info):
    """Return expected checksum tuple (algorithm, value) from Modrinth file metadata."""
    hashes = getattr(file_info, 'hashes', None)
    if not hashes:
        return None, None

    if isinstance(hashes, dict):
        hash_map = hashes
    else:
        hash_map = {}
        for algorithm in ('sha1', 'sha512', 'sha256'):
            hash_value = getattr(hashes, algorithm, None)
            if hash_value:
                hash_map[algorithm] = hash_value

    for algorithm in ('sha1', 'sha512', 'sha256'):
        hash_value = hash_map.get(algorithm)
        if hash_value:
            return algorithm, hash_value

    return None, None


def calculate_file_hash(file_path, algorithm):
    hasher = hashlib.new(algorithm)
    with open(file_path, 'rb') as file_handle:
        for chunk in iter(lambda: file_handle.read(8192), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


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
    expected_hash_algorithm, expected_hash_value = get_expected_hash(primary_file)

    if os.path.exists(dest_path):
        if expected_hash_algorithm and expected_hash_value:
            existing_hash_value = calculate_file_hash(dest_path, expected_hash_algorithm)
            if existing_hash_value == expected_hash_value:
                logger.info(f"Datapack '{filename}' already exists at '{dest_path}' with valid checksum, skipping download")
                return False

            logger.warning(f"Datapack '{filename}' exists at '{dest_path}' but checksum mismatch, re-downloading")
            os.remove(dest_path)
        else:
            logger.info(f"Datapack '{filename}' already exists at '{dest_path}', skipping download")
            return False

    logger.info(f"Downloading '{filename}' from {download_url}...")
    response = requests.get(download_url, stream=True)
    response.raise_for_status()

    download_hasher = hashlib.new(expected_hash_algorithm) if expected_hash_algorithm else None
    with open(dest_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if not chunk:
                continue
            f.write(chunk)
            if download_hasher:
                download_hasher.update(chunk)

    if download_hasher and expected_hash_value:
        downloaded_hash_value = download_hasher.hexdigest()
        if downloaded_hash_value != expected_hash_value:
            os.remove(dest_path)
            raise Exception(
                f"Checksum mismatch for datapack '{datapack_slug}' file '{filename}': expected "
                f"{expected_hash_algorithm}={expected_hash_value}, got {downloaded_hash_value}"
            )

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
