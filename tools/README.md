# CCSDK parent tools

## migrateOdl.py

This script tries to generate the ccsdk odl parents out of the existing odl parents and a downloaded and extracted odl folder.

Usage

```
$ python3 tools/migrateOdlParents.py --src ~/Downloads/karaf-0.15.1
```

args:

 * --src  opendaylight source folder
 * --group-id parent group-id to set (default=org.onap.ccsdk.parent)
 * --version parent version to set
 * --non-strict  flag to stop on fail (default=True)


## mkbom.sh

This script searches for all artifacts in the local odl repository folder $ODL_HOME/system and writes out of this a pom file. This is used to generate the installed-odl-bom/pom.xml.

Usage:

```
$ cd ~/Downloads/opendaylight-15.0.0/system
$ ./your-path-to-odl-parents/tools/mkbom.sh your-group-id  your-artifact-id your-version > /your-path-to-odl-parents/installed-odl-bom/pom.xml
```