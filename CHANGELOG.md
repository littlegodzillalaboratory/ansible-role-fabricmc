# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 1.2.0 - 2026-02-21
### Added
- Add fabmc_fabric_mods_download_delay config
- Add datapacks provisioning support
- Add fabmc_fabric_datapacks config
- Add fabmc_fabric_datapacks_download_delay config
- Add checksum verification for downloaded mods and datapacks

### Changed
- Improve mods cleanup prior to installation

## 1.1.0 - 2026-02-18
### Added
- Add Fabric API provisioning support
- Add Fabric mods provisioning support

### Changed
- Update MDH to Cobbler

## 1.0.0 - 2025-11-29
### Added
- Add fabmc_server_properties configuration for setting server.properties values
- Add systemd service support
- Add noble to supported Ubuntu platform
- Add status, start-log, conf, log utility aliases
- Add shebang to start shell script
- Add fabmc_env_path configuration for setting systemd service environment PATH
- Add fabmc_eula_accepted configuration

### Changed
- Use MDH as Makefile standard
- Shift Github ID and Galaxy namespace to littlegodzillalaboratory
- Restructure Molecule files to work with latest Molecule 25.9.0
- Change molecule config to use role namespace and name instead of workspace

## 0.10.0 - 2025-02-22
### Added
- Initial version
