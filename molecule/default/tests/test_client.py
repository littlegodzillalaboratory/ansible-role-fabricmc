import pytest

def test_fabricmc_client_dir(host):

    fabmc_client_dir = host.file('/root/.minecraft')
    assert fabmc_client_dir.exists
    assert fabmc_client_dir.is_directory
    assert fabmc_client_dir.mode == 0o755

def test_client_bin_dir(host):

    client_bin_dir = host.file('/root/.minecraft/bin')
    assert client_bin_dir.exists
    assert client_bin_dir.is_directory
    assert client_bin_dir.mode == 0o755

def test_client_mods_dir(host):

    client_mods_dir = host.file('/root/.minecraft/mods')
    assert client_mods_dir.exists
    assert client_mods_dir.is_directory
    assert client_mods_dir.mode == 0o755

def test_installer_jar_file(host):

    installer_jar_file = host.file('/root/.minecraft/bin/fabric-installer-1.0.1.jar')
    assert installer_jar_file.exists
    assert installer_jar_file.is_file
    assert installer_jar_file.mode == 0o644

def test_installer_jar_symlink(host):

    installer_jar_symlink = host.file('/root/.minecraft/bin/fabric-installer.jar')
    assert installer_jar_symlink.exists
    assert installer_jar_symlink.is_symlink

def test_fabric_installer_install_script(host):

    install_script = host.file('/root/.minecraft/bin/install.sh')
    assert install_script.exists
    assert install_script.is_file
    assert install_script.mode == 0o755
    assert install_script.contains('java -jar "~/.minecraft//bin/fabric-installer.jar" client -mcversion 1.21.4 -dir "~/.minecraft/"')

def test_fabric_api_mod_file(host):

    result = host.run(
        "find /root/.minecraft/mods -maxdepth 1 -type f -name 'fabric-api-*.jar'"
    )
    assert result.rc == 0

    fabric_api_mod_paths = [path for path in result.stdout.splitlines() if path]
    assert len(fabric_api_mod_paths) > 0

    fabric_api_mod_file = host.file(fabric_api_mod_paths[0])
    assert fabric_api_mod_file.exists
    assert fabric_api_mod_file.is_file
    assert fabric_api_mod_file.mode == 0o644
