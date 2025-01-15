#!/usr/bin/python3
import os
import argparse
import subprocess
import re
import shutil
import tempfile
from lib.pomfile import PomFile

DEFAULT_PARENT_GROUPID="org.onap.ccsdk.parent"
DEFAULT_PARENT_VERSION="2.7.0-SNAPSHOT"
DEFAULT_STRICT=True
USE_OLD_SERVLET_API=True

class OdlParentMigrator:

    def __init__(self,odlSourcePath, odlParentPath=None, groupId=DEFAULT_PARENT_GROUPID, version=DEFAULT_PARENT_VERSION, strict=DEFAULT_STRICT):
        self.odlSourcePath=odlSourcePath
        self.mvnbin = "/usr/bin/mvn"
        self.version = version
        self.groupId = groupId
        self.strict = strict
        if odlParentPath is None:
            odlParentPath = os.path.abspath(os.path.dirname(os.path.realpath(__file__))+"/../odlparent")
        self.odlParentPath=odlParentPath
        self.parentPath =os.path.abspath(odlParentPath+'/../') 


    def getMvnRepoVersion(self, groupId, artifactId):
        path="{}/system/{}/{}".format(self.odlSourcePath,groupId.replace('.','/'),artifactId)
        if not os.path.exists(path):
            return None
        folders =[f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
        if len(folders)<1:
            return None
        return folders[0]
    
    def getMvnRepoVersions(self, groupId, artifactId):
        path="{}/system/{}/{}".format(self.odlSourcePath,groupId.replace('.','/'),artifactId)
        if not os.path.exists(path):
            return None
        folders =[f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
        if len(folders)<1:
            return None
        return folders

    def migrateInstalledOdlBom(self) -> bool:
        success = True
        print("migrating installed-odl-bom")
        root=os.path.abspath(self.odlParentPath+'/..')
        self.exec(('cd {src}/system && '+
            '{root}/tools/mkbom.sh {groupId} {artifactId} {version}> '+
            '{root}/installed-odl-bom/pom.xml && cd -').format(
            root=root,src=self.odlSourcePath,
            parent=self.odlParentPath,groupId=self.groupId,
            artifactId='installed-odl-bom', version=self.version))
        if USE_OLD_SERVLET_API:
            pom = PomFile('{}/installed-odl-bom/pom.xml'.format(root))
            success = pom.setDependencyManagementVersion('javax.servlet','javax.servlet-api','3.1.0')

        print("done")
        return success

    def migrateDependenciesBom(self) -> bool:
        success = True
        print("migrating dependencies-bom")
    
        print("done" if success else "failed")
        return success

    def migrateSetupProperties(self) -> bool:
        success = True
        print("migrating setup")
        mdsalVersion=self.getMvnRepoVersion('org.opendaylight.mdsal','mdsal-binding-api')
        odlBundleVersion=self.getMvnRepoVersion('org.opendaylight.odlparent','features-odlparent')
        mdsalItVersion=self.getMvnRepoVersion('org.opendaylight.controller','features-controller')
        yangVersion = self.getMvnRepoVersion('org.opendaylight.yangtools','yang-common')
        self.replaceInFile(self.odlParentPath+'/setup/src/main/properties/binding-parent.properties',
            'odlparent.version=.*','odlparent.version={}'.format(mdsalVersion))
        self.replaceInFile(self.odlParentPath+'/setup/src/main/properties/bundle-parent.properties',
            'odlparent.version=.*','odlparent.version={}'.format(odlBundleVersion))
        self.replaceInFile(self.odlParentPath+'/setup/src/main/properties/feature-repo-parent.properties',
            'odlparent.version=.*','odlparent.version={}'.format(odlBundleVersion))
        self.replaceInFile(self.odlParentPath+'/setup/src/main/properties/karaf4-parent.properties',
            'odlparent.version=.*','odlparent.version={}'.format(odlBundleVersion))
        self.replaceInFile(self.odlParentPath+'/setup/src/main/properties/mdsal-it-parent.properties',
            'odlparent.version=.*','odlparent.version={}'.format(mdsalItVersion))
        self.replaceInFile(self.odlParentPath+'/setup/src/main/properties/odlparent-lite.properties',
            'odlparent.version=.*','odlparent.version={}'.format(odlBundleVersion))
        self.replaceInFile(self.odlParentPath+'/setup/src/main/properties/odlparent.properties',
            'odlparent.version=.*','odlparent.version={}'.format(odlBundleVersion))
        self.replaceInFile(self.odlParentPath+'/setup/src/main/properties/single-feature-parent.properties',
            'odlparent.version=.*','odlparent.version={}'.format(odlBundleVersion))


        templatePom = PomFile(self.odlParentPath+'/setup/src/main/resources/pom-template.xml')
        # x = templatePom.setXmlValue('/project/properties/odl.controller.mdsal.version',mdsalVersion)
        # success = success and x
        x = templatePom.setXmlValue('/project/properties/odl.mdsal.version',odlBundleVersion)
        success = success and x
        x = templatePom.setXmlValue('/project/properties/odl.mdsal.model.version',odlBundleVersion)
        success = success and x
        x = templatePom.setXmlValue('/project/properties/odl.netconf.restconf.version',mdsalVersion)
        success = success and x
        x = templatePom.setXmlValue('/project/properties/odl.netconf.netconf.version',mdsalVersion)
        success = success and x
        x = templatePom.setXmlValue('/project/properties/odl.netconf.sal.rest.docgen.version',mdsalVersion)
        success = success and x
        
        x = templatePom.setXmlValue('/project/properties/commons.codec.version',
            self.getMvnRepoVersion('commons-codec','commons-codec'))
        success = success and x
        x = templatePom.setXmlValue('/project/properties/commons.lang3.version',
            self.getMvnRepoVersion('org.apache.commons','commons-lang3'))
        success = success and x
        x = templatePom.setXmlValue('/project/properties/commons.lang.version',
            self.getMvnRepoVersion('commons-lang','commons-lang'))
        success = success and x
        x = templatePom.setXmlValue('/project/properties/commons.net.version',
            self.getMvnRepoVersion('commons-net','commons-net'))
        success = success and x
        x = templatePom.setXmlValue('/project/properties/eclipse.persistence.version',
            self.getMvnRepoVersion('org.eclipse.persistence','org.eclipse.persistence.core'))
        success = success and x
        x = templatePom.setXmlValue('/project/properties/gson.version',
            self.getMvnRepoVersion('com.google.code.gson','gson'))
        success = success and x
        x = templatePom.setXmlValue('/project/properties/guava.version',
            self.getMvnRepoVersion('com.google.guava','guava'))
        success = success and x
        x = templatePom.setXmlValue('/project/properties/jackson.version',
            self.getMvnRepoVersion('com.fasterxml.jackson.core','jackson-core'))
        success = success and x
        x = templatePom.setXmlValue('/project/properties/javassist.version',
            self.getMvnRepoVersion('org.javassist','javassist'))
        success = success and x
        x = templatePom.setXmlValue('/project/properties/jersey.version',
            self.getMvnRepoVersion('org.glassfish.jersey.core','jersey-common'))
        success = success and x
        x = templatePom.setXmlValue('/project/properties/jersey.client.version',
            self.getMvnRepoVersion('org.glassfish.jersey.core','jersey-client'))
        success = success and x
        x = templatePom.setXmlValue('/project/properties/org.json.version',
            self.getMvnRepoVersion('org.json','json'))
        success = success and x
        x = templatePom.setXmlValue('/project/properties/netty.version',
            self.getMvnRepoVersion('io.netty','netty-common'))
        success = success and x
        x = templatePom.setXmlValue('/project/properties/slf4j.version',
            self.getMvnRepoVersion('org.slf4j','slf4j-api'))
        success = success and x
        x = templatePom.setXmlValue('/project/properties/derby.version',
            self.getMvnRepoVersion('org.apache.derby','derby'))
        success = success and x
        x = templatePom.setXmlValue('/project/properties/jetty.version',
            self.getMvnRepoVersion('org.eclipse.jetty','jetty-http'))        
        success = success and x
        print("done" if success else "failed")
        return success

    def migrateDependenciesOdlBom(self):
        success = True
        print("migrating dependencies-odl-bom")
        bgpVersion = self.getMvnRepoVersion('org.opendaylight.bgpcep','topology-api')
        controllerVersion = self.getMvnRepoVersion('org.opendaylight.controller', 'blueprint')
        mdsalVersion=self.getMvnRepoVersion('org.opendaylight.mdsal','mdsal-binding-api')
        netconfVersion = self.getMvnRepoVersion('org.opendaylight.netconf','netconf-api')

        pomFile = PomFile(os.path.abspath(self.parentPath+'/dependencies-odl-bom/pom.xml'))
        x = pomFile.setXmlValue('/project/version',self.version)
        success = success and x
        x = pomFile.setXmlValue('/project/dependencyManagement/dependencies/dependency[artifactId=bgpcep-artifacts]/version',bgpVersion)
        success = success and x
        x = pomFile.setXmlValue('/project/dependencyManagement/dependencies/dependency[artifactId=controller-artifacts]/version',controllerVersion)
        success = success and x
        x = pomFile.setXmlValue('/project/dependencyManagement/dependencies/dependency[artifactId=mdsal-artifacts]/version',mdsalVersion)
        success = success and x
        # x = pomFile.setXmlValue('/project/dependencyManagement/dependencies/dependency[artifactId=netconf-artifacts]/version',netconfVersion)
        # success = success and x
        # x = pomFile.setXmlValue('/project/dependencyManagement/dependencies/dependency[artifactId=sal-binding-broker-impl]/version',netconfVersion, True)
        # success = success and x
        # at the moment not possible because of dependent variable in path after value to set
        # x = pomFile.setXmlValue('/project/dependencyManagement/dependencies/dependency[artifactId=sal-binding-broker-impl,type=test-jar]/version',netconfVersion)
        # success = success and x
        # x = pomFile.setXmlValue('/project/dependencyManagement/dependencies/dependency[artifactId=sal-test-model]/version',netconfVersion)
        # success = success and x
        print("done" if success else "failed")
        return success

    def setParentValues(self):
        print("setting all other parents")
        # find all pom.xml files with parent to set
        pomfiles=[os.path.abspath(self.parentPath+'/pom.xml'),
            os.path.abspath(self.parentPath+'/dependencies-bom/pom.xml'),
            os.path.abspath(self.odlParentPath+'/pom.xml'),
            os.path.abspath(self.odlParentPath+'/setup/pom.xml'),
            os.path.abspath(self.parentPath+'/springboot/pom.xml'),
            os.path.abspath(self.parentPath+'/springboot/spring-boot-setup/pom.xml')]
        
        subs = os.listdir(os.path.abspath(self.parentPath+'/springboot'))
        for sub in subs:
            if sub.startswith('springboot'):
                pomfiles.append(self.parentPath+'/springboot/'+sub+'/pom.xml')
                          
        success=True
        for file in pomfiles:
            pomfile = PomFile(file)
            if pomfile.hasParent():
                x = pomfile.setXmlValue('/project/parent/groupId',self.groupId)
                success = success and x
                x = pomfile.setXmlValue('/project/parent/version',self.version)
                success = success and x
            
        # find all pom.xml files with groupId and version to set
        pomfiles=PomFile.findAll(os.path.abspath(self.odlParentPath+'/..'))
        for file in pomfiles:
            pomfile = PomFile(file)
            x = pomfile.setXmlValue('/project/groupId',self.groupId)
            success = success and x
            x = pomfile.setXmlValue('/project/version',self.version)
            success = success and x
        
        # set only groupId for odl template
        pomfile = PomFile(self.odlParentPath+'/setup/src/main/resources/pom-template.xml')
        x = pomfile.setXmlValue('/project/groupId',self.groupId)
        success = success and x
        print("done" if success else "failed")
        return success
        
    def execMaven(self, command):
        print(self.execToStdOut(self.mvnbin,command))


        

    '''
    Perform the pure-Python equivalent of in-place `sed` substitution: e.g.,
    `sed -i -e 's/'${pattern}'/'${repl}' "${filename}"`.
    '''
    def replaceInFile(self, filename, pattern, replacement):
   
        # For efficiency, precompile the passed regular expression.
        pattern_compiled = re.compile(pattern)

        # For portability, NamedTemporaryFile() defaults to mode "w+b" (i.e., binary
        # writing with updating). This is usually a good thing. In this case,
        # however, binary writing imposes non-trivial encoding constraints trivially
        # resolved by switching to text writing. Let's do that.
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
            with open(filename) as src_file:
                for line in src_file:
                    tmp_file.write(pattern_compiled.sub(replacement, line))

        # Overwrite the original file with the munged temporary file in a
        # manner preserving file attributes (e.g., permissions).
        shutil.copystat(filename, tmp_file.name)
        shutil.move(tmp_file.name, filename)

    def exec(self, bin, params=""):
        output = subprocess.Popen(
            bin+" "+params, shell=True, stdout=subprocess.PIPE).stdout.read()
        return output
    def execToStdOut(self, bin, params=""):
        process = subprocess.Popen(
            (bin+" "+params).split(' '), shell=False)
        process.communicate()
    
    def run(self):
        print("starting ONAP odl parent migration")
        print("odl src={}".format(self.odlSourcePath))
        print("target ={}".format(self.odlParentPath))
        x = self.migrateInstalledOdlBom()
        if self.strict and not x:
            exit(1)
        x = self.migrateDependenciesBom()
        if self.strict and not x:
            exit(1)
        x = self.migrateDependenciesOdlBom()
        if self.strict and not x:
            exit(1)
        x = self.migrateSetupProperties()
        if self.strict and not x:
            exit(1)
        x = self.setParentValues()
        if self.strict and not x:
            exit(1)
#        self.execMaven('clean install -f {}'.format(self.odlParentPath+'/setup'))
#        self.execMaven('clean install -f {}'.format(self.parentPath))

parser = argparse.ArgumentParser(description='ONAP odl parent migration tool')
parser.add_argument('--src', type=str, required=True, help='the source folder where odl is located')
parser.add_argument('--group-id', type=str, required=False,default=DEFAULT_PARENT_GROUPID, help='groupid for the parents')
parser.add_argument('--version', type=str, required=False,default=DEFAULT_PARENT_VERSION, help='version')
parser.add_argument('--non-strict', action='store_false' if DEFAULT_STRICT else 'store_true', help='determine stopping script if something cannot be set')
args = parser.parse_args()

migrator = OdlParentMigrator(args.src,None,args.group_id, args.version, args.non_strict)
migrator.run()