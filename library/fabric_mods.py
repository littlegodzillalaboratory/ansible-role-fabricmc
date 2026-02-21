#!/usr/bin/python

DOCUMENTATION = r'''
---
module: fabric_mods
short_description: Install Fabric mods
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
    'format': "[fabric-mods] [%(levelname)s] [%(asctime)s] %(message)s",
    'level': "debug"
}
cfl = Conflog(conf_dict=conf_dict)
logger = cfl.get_logger('fabric_mods')


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

def download_mod(client, mod_slug, loader, game_version, dest_dir):
    """Download a mod from Modrinth using modrinth-api-wrapper.
    
    Returns True if a mod was downloaded, False if it already existed.
    """
    logger.info(f"Fetching project versions for '{mod_slug}'...")
    
    # Get all versions for the project
    versions = client.list_project_versions(mod_slug)
    
    # Filter versions by loader and game version
    compatible_versions = [
        v for v in versions
        if loader in v.loaders and game_version in v.game_versions
    ]
    
    if not compatible_versions:
        raise Exception(f"No compatible version found for mod '{mod_slug}' with Minecraft {game_version} and loader {loader}")
    
    # Get the latest compatible version (first in the list) of the mod
    version = compatible_versions[0]
    
    # Find the primary file of the mod
    primary_file = None
    for file in version.files:
        if file.primary:
            primary_file = file
            break
    
    if not primary_file:
        primary_file = version.files[0] if version.files else None
    
    if not primary_file:
        raise Exception(f"No downloadable file found for mod '{mod_slug}'")
    
    download_url = primary_file.url
    filename = primary_file.filename
    dest_path = os.path.join(dest_dir, filename)
    expected_hash_algorithm, expected_hash_value = get_expected_hash(primary_file)

    # Skip download if the mod file already exists and checksum is valid
    if os.path.exists(dest_path):
        if expected_hash_algorithm and expected_hash_value:
            existing_hash_value = calculate_file_hash(dest_path, expected_hash_algorithm)
            if existing_hash_value == expected_hash_value:
                logger.info(f"Mod '{filename}' already exists at '{dest_path}' with valid checksum, skipping download")
                return False

            logger.warning(f"Mod '{filename}' exists at '{dest_path}' but checksum mismatch, re-downloading")
            os.remove(dest_path)
        else:
            logger.info(f"Mod '{filename}' already exists at '{dest_path}', skipping download")
            return False

    # Download the mod file
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
                f"Checksum mismatch for mod '{mod_slug}' file '{filename}': expected "
                f"{expected_hash_algorithm}={expected_hash_value}, got {downloaded_hash_value}"
            )

    logger.info(f"Successfully downloaded '{filename}' to '{dest_path}'")
    return True

def main():

    module_args = dict(
        minecraft_version=dict(type="str", required=True),
        mods=dict(type="list", elements="str", required=True),
        mods_download_delay=dict(type="int", required=True),
        install_dir=dict(type="str", required=True),
    )
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    minecraft_version = module.params["minecraft_version"]
    mods = module.params["mods"]
    mods_download_delay = module.params["mods_download_delay"]
    install_dir = module.params["install_dir"]

    logger.info(f"'{len(mods)}' Fabric mod(s) to be installed for Minecraft version '{minecraft_version}'...")

    client = Client()
    mods_dir = os.path.join(install_dir, "workspace", "mods")

    changed = False
    for mod in mods:
        logger.info(f"Installing Fabric mod '{mod}'...")
        if download_mod(client, mod, "fabric", minecraft_version, mods_dir):
            changed = True
        time.sleep(mods_download_delay)

    result = {
        "changed": changed,
    }
    module.exit_json(**result)

if __name__ == "__main__":
    main()
