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
        fabmc_install_dir: /opt/fabricmc
        fabmc_java_opts: -Xmx2048M -Xms1024M

      roles:
        - cliffano.fabricmc

For convenience, add aliases for starting and stopping the server, editing server.properties, and tailing the server log:

    alias fabricmc-start='cd <fabmc_install_dir>/workspace && nohup <fabmc_install_dir>/bin/start.sh > /var/log/fabricmc/fabricmc.log &'
    alias fabricmc-stop='pkill java' # temporary, will have to handle specific java process from fabricmc-start PID
    alias fabricmc-conf='vi <fabmc_install_dir>/workspace/server.properties'
    alias fabricmc-log='tail -f <fabmc_install_dir>/workspace/logs/latest.log'

Config
------

When the server is started the very first time, you'll encounter a warning message about EULA:

    [11:54:56] [main/WARN]: Failed to load eula.txt
    [11:54:56] [main/INFO]: You need to agree to the EULA in order to run the server. Go to eula.txt for more info.

Open the configuration file at `<fabmc_install_dir>/workspace/server.properties`:

    #By changing the setting below to TRUE you are indicating your agreement to our EULA (https://aka.ms/MinecraftEULA).
    #Sat Feb 15 11:54:56 UTC 2025
    eula=false

and then replace `eula=false` with `eula=true`.