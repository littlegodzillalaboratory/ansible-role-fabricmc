<img align="right" src="https://raw.github.com/littlegodzillalaboratory/ansible-role-fabricmc/main/avatar.jpg" alt="Avatar"/>

[![Build Status](https://github.com/littlegodzillalaboratory/ansible-role-fabricmc/workflows/CI/badge.svg)](https://github.com/littlegodzillalaboratory/ansible-role-fabricmc/actions?query=workflow%3ACI)
[![Security Status](https://snyk.io/test/github/cliffano/ansible-role-fabricmc/badge.svg)](https://snyk.io/test/github/cliffano/ansible-role-fabricmc)
<br/>

Ansible Role FabricMC
---------------------

Ansible Role FabricMC is an Ansible role for provisioning [Fabric mod loader](https://fabricmc.net/) for Minecraft .

Usage
-----

Use the role in your playbook:

    - hosts: all

      vars:
        fabmc_minecraft_version: '1.21.4'
        fabmc_fabric_loader_version: '0.16.10'
        fabmc_installer_version: '1.0.1'
        fabmc_fabric_api_version: '0.119.4+1.21.4'
        fabmc_fabric_mods:
          - sodium
          - ferrite-core
          - lithium
        fabmc_fabric_mods_download_delay: 2
        fabmc_install_dir: /opt/fabricmc
        fabmc_install_id: minecraft-java
        fabmc_os_user: minecraft
        fabmc_java_opts: -Xmx2048M -Xms1024M
        fabmc_eula_accepted: true
        fabmc_server_properties:
          motd: "A Minecraft Server with Fabric mod loader managed by Ansible Role FabricMC"

      roles:
        - littlegodzillalaboratory.fabricmc

Or alternatively, as a task using import role:

      tasks:

        - ansible.builtin.pip:
            name: pip
            virtualenv: "{{ ansible_user_dir }}/.virtualenvs/fabricmc"
            virtualenv_command: python3 -m venv
            state: latest
          run_once: true

        - ansible.builtin.pip:
            name:
              - conflog
              - modrinth-api-wrapper
              - requests
            virtualenv: "{{ ansible_user_dir }}/.virtualenvs/fabricmc"
            state: present
          run_once: true
          
        - ansible.builtin.import_role:
            name: littlegodzillalaboratory.fabricmc
          vars:
            fabmc_minecraft_version: '1.21.4'
            fabmc_fabric_loader_version: '0.16.10'
            fabmc_installer_version: '1.0.1'
            fabmc_fabric_api_version: '0.119.4+1.21.4'
            fabmc_fabric_mods:
              - sodium
              - ferrite-core
              - lithium
            fabmc_fabric_mods_download_delay: 2
            fabmc_install_dir: /opt/fabricmc
            fabmc_install_id: minecraft-java
            fabmc_os_user: minecraft
            fabmc_java_opts: -Xmx2048M -Xms1024M
            fabmc_eula_accepted: true
            fabmc_server_properties:
              motd: "A Minecraft Server with Fabric mod loader managed by Ansible Role FabricMC"
          environment:
            PATH: "{{ ansible_user_dir }}/.virtualenvs/fabricmc/bin:{{ ansible_env.PATH }}"
            VIRTUAL_ENV: "{{ ansible_user_dir }}/.virtualenvs/fabricmc"

On machines with systemd, a `<fabmc_install_id>` service will be provisioned so you can use systemctl to manage the server.

    systemctl start <fabmc_install_id>.service
    systemctl stop <fabmc_install_id>.service
    systemctl status <fabmc_install_id>.service

The following aliases are also provisioned to simplify the maintenance of FabricMC server:

| Alias | Command | Description |
|-------|---------|-------------|
| <fabmc_install_id>-conf | `vi <fabmc_install_dir>/workspace/server.properties` | Open up server.properties using `vi` |
| <fabmc_install_id>-log | `tail -f <fabmc_install_dir>/workspace/logs/latest.log` | Tail the latest server log |
| <fabmc_install_id>-start | `systemctl start <fabmc_install_id>.service` | Start the server |
| <fabmc_install_id>-stop | `systemctl stop <fabmc_install_id>.service` | Stop the server |
| <fabmc_install_id>-status | `systemctl status <fabmc_install_id>.service` | Check the status of the server |
| <fabmc_install_id>-start-log | `journalctl -u <fabmc_install_id>` | Show the server start log |

Config
------

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| fabmc_minecraft_version | [Supported Minecraft version number](https://github.com/littlegodzillalaboratory/ansible-role-minecraft-java/blob/main/vars/main.yml#L2) | `1.21` |  `1.21.10` |
| fabmc_fabric_loader_version | [Fabric loader version number](https://maven.fabricmc.net/net/fabricmc/fabric-loader/) | `0.16.10` |  `1.18.1` |
| fabmc_installer_version | [Fabric installer version number](https://maven.fabricmc.net/net/fabricmc/fabric-installer/) | `1.0.1` |  `1.1.0` |
| fabmc_fabric_api_version | [Fabric API version number](https://modrinth.com/mod/fabric-api) | `0.119.4+1.21.4` |  `0.105.4+1.21.2` |
| fabmc_fabric_mods | [Fabric mods](https://modrinth.com/discover/mods) | - sodium<br/>- ferrite-core<br/>- lithium | |
| fabmc_fabric_mods_download_delay | Delay period (in seconds) between Fabric mod file downloads | 2 | 10 |
| fabmc_install_id | Minecraft Fabric mod loader installation ID, useful to distinguish multiple installations on the same machine | `fabricmc` | `fabricmc-1` |
| fabmc_install_dir | Minecraft Fabric mod loader installation directory | `/opt/fabricmc` | `/some/other/path` |
| fabmc_os_user | System user which the Java process runs under | `fabricmc` | `someuser` |
| fabmc_env_path | To be used as the [environment PATH](https://en.wikipedia.org/wiki/PATH_(variable)) which the FabricMC server runs with. Must have `java` command under one of the path values. | `/usr/local/sbin:/usr/local/bin:`<br/>`/usr/sbin:/usr/bin:/sbin:/bin` | `/home/someuser/.sdkman/candidates/java/current/bin:`<br/>`/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin` |
| fabmc_java_opts | Server [Java options](https://www.theserverside.com/blog/Coffee-Talk-Java-News-Stories-and-Opinions/jvm-options-java-parameters-command-line-environment-variable-list-xms-xmx-memory) | `-Xmx2048M -Xms1024M` | `-Xmx2048M -Xms1024M` |
| fabmc_eula_accepted | Accept the Minecraft [EULA](https://nodecraft.com/support/games/minecraft/general/minecraft-eula) when set to true | `true` | `false` |
| fabmc_server_properties | Minecraft [server properties](https://minecraft.fandom.com/wiki/Server.properties) key-value pairs. | `motd: "A Minecraft Server with Fabric mod loader managed by Ansible Role FabricMC"` | `difficulty: normal`<br/>`gamemode: survival`<br/>`hardcore: "false"` |
