import pytest

def test_fabricmc_install_dir(host):

    fabmc_install_dir = host.file('/opt/fabricmc')
    assert fabmc_install_dir.exists
    assert fabmc_install_dir.is_directory
    assert fabmc_install_dir.mode == 0o755

def test_install_bin_dir(host):

    install_bin_dir = host.file('/opt/fabricmc/bin')
    assert install_bin_dir.exists
    assert install_bin_dir.is_directory
    assert install_bin_dir.mode == 0o755

def test_install_workspace_dir(host):

    install_workspace_dir = host.file('/opt/fabricmc/workspace')
    assert install_workspace_dir.exists
    assert install_workspace_dir.is_directory
    assert install_workspace_dir.mode == 0o755

def test_server_launcher_jar_file(host):

    server_jar_file = host.file('/opt/fabricmc/bin/minecraft_server_launcher.1.21.4-0.16.10-1.0.1.jar')
    assert server_jar_file.exists
    assert server_jar_file.is_file
    assert server_jar_file.mode == 0o644

def test_server_launcher_jar_symlink(host):

    server_jar_symlink = host.file('/opt/fabricmc/bin/minecraft_server_launcher.jar')
    assert server_jar_symlink.exists
    assert server_jar_symlink.is_symlink

def test_eula_file(host):

    eula_file = host.file('/opt/fabricmc/workspace/eula.txt')
    assert eula_file.exists
    assert eula_file.is_file
    assert eula_file.mode == 0o644
    assert eula_file.contains('eula=true')

def test_server_launcher_properties_file(host):

    server_properties_file = host.file('/opt/fabricmc/workspace/server.properties')
    assert server_properties_file.exists
    assert server_properties_file.is_file
    assert server_properties_file.mode == 0o644
    assert server_properties_file.contains('motd=A Minecraft Server with Fabric mod loader managed by Ansible Role FabricMC')


def test_server_launcher_start_script(host):

    server_start_script = host.file('/opt/fabricmc/bin/start.sh')
    assert server_start_script.exists
    assert server_start_script.is_file
    assert server_start_script.mode == 0o755
    assert server_start_script.contains('java -Xmx2048M -Xms1024M -jar /opt/fabricmc/bin/minecraft_server_launcher.jar nogui')

def test_server_launcher_service_file(host):

    server_service_file = host.file('/etc/systemd/system/fabricmc.service')
    assert server_service_file.exists
    assert server_service_file.is_file
    assert server_service_file.mode == 0o644
    assert server_service_file.contains('Description=Minecraft Java with Fabric')
    assert server_service_file.contains('User=fabricmc')
    assert server_service_file.contains('ExecStart=/opt/fabricmc/bin/start.sh')

def test_fabric_launcher_service(host):
    fabric_service = host.service('fabricmc')
    # Can't test service enabled state due to test running within container
    # assert fabric_service.is_enabled
    assert not fabric_service.is_running

def test_aliases_for_minecraft_server_generic_utilities(host):

    # TODO: Update file path when test container switches to non-root user
    aliases_file = host.file('/root/.bash_aliases')
    assert aliases_file.exists
    assert aliases_file.is_file
    assert aliases_file.mode == 0o644
    assert aliases_file.contains('alias fabricmc-conf="vi /opt/fabricmc/workspace/server.properties"')
    assert aliases_file.contains('alias fabricmc-log="tail -f /opt/fabricmc/workspace/logs/latest.log"')

def test_fabric_api_mod_file(host):

    result = host.run(
        "find /opt/fabricmc/workspace/mods -maxdepth 1 -type f -name 'fabric-api-*.jar'"
    )
    assert result.rc == 0

    fabric_api_mod_paths = [path for path in result.stdout.splitlines() if path]
    assert len(fabric_api_mod_paths) > 0

    fabric_api_mod_file = host.file(fabric_api_mod_paths[0])
    assert fabric_api_mod_file.exists
    assert fabric_api_mod_file.is_file
    assert fabric_api_mod_file.mode == 0o644

def test_fabric_mods_files(host):

    result = host.run(
        "find /opt/fabricmc/workspace/mods -maxdepth 1 -type f -name '*.jar' ! -name 'fabric-api-*.jar'"
    )
    assert result.rc == 0

    mod_paths = [path for path in result.stdout.splitlines() if path]
    assert len(mod_paths) > 0

    default_mod_slugs = [
        'sodium',
        'ferrite-core',
        'lithium',
    ]

    def normalize_letters(value):
        return ''.join(ch for ch in value.lower() if ch.isalpha())

    normalized_default_mod_slugs = [
        normalize_letters(mod_slug)
        for mod_slug in default_mod_slugs
    ]

    for mod_path in mod_paths:
        mod_file = host.file(mod_path)
        assert mod_file.exists
        assert mod_file.is_file
        assert mod_file.mode == 0o644

        mod_name = mod_path.rsplit('/', 1)[-1].rsplit('.', 1)[0]
        normalized_mod_name = normalize_letters(mod_name)
        assert any(
            normalized_mod_name.startswith(default_mod_slug)
            for default_mod_slug in normalized_default_mod_slugs
        ), f"Unexpected Fabric mod file: {mod_path}"

def test_fabric_datapacks_files(host):
    
    result = host.run(
        "find /opt/fabricmc/workspace/world/datapacks -maxdepth 1 -type f -name '*.zip'"
    )
    assert result.rc == 0

    datapack_paths = [path for path in result.stdout.splitlines() if path]
    assert len(datapack_paths) > 0

    default_datapack_slugs = [
        'terralith',
    ]

    def normalize_letters(value):
        return ''.join(ch for ch in value.lower() if ch.isalpha())

    normalized_default_datapack_slugs = [
        normalize_letters(datapack_slug)
        for datapack_slug in default_datapack_slugs
    ]

    for datapack_path in datapack_paths:
        datapack_file = host.file(datapack_path)
        assert datapack_file.exists
        assert datapack_file.is_file
        assert datapack_file.mode == 0o644

        datapack_name = datapack_path.rsplit('/', 1)[-1].rsplit('.', 1)[0]
        normalized_datapack_name = normalize_letters(datapack_name)
        assert any(
            normalized_datapack_name.startswith(default_datapack_slug)
            for default_datapack_slug in normalized_default_datapack_slugs
        ), f"Unexpected Fabric datapack file: {datapack_path}"