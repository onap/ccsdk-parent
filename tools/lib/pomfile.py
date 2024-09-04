import re
import tempfile
import tempfile
import glob
import shutil
from .xpath import XPath

class PomFile:

    def __init__(self, filename):
        self.filename=filename

    def hasParent(self) -> bool:
        pattern_compiled = re.compile('<project[>\ ]')
        inProject=False
        with open(self.filename,'r') as src_file:
                for line in src_file:
                    m = pattern_compiled.search(line)
                    if m is not None:
                        if inProject == True:
                            return True
                        inProject=True
                        pattern_compiled = re.compile('<parent[>\ ]')
        return False
                    

    def setDependencyVersion(self, groupId, artifactId, version) -> bool:
        return self.setXmlValue('/project/dependencies/dependency[groupId={},artifactId={}]/version'.format(groupId,artifactId),version)
    def setDependencyManagementVersion(self, groupId, artifactId, version) -> bool:
        return self.setXmlValue('/project/dependencyManagement/dependencies/dependency[groupId={},artifactId={}]/version'.format(groupId,artifactId),version)
    # set xmlElementValue (just simple values - no objects)
    # valuePath: xpath
    #    e.g. /project/parent/version
    #         /project/dependencies/dependency[groupId=org.opendaylight.netconf]/version
    # value: value to set
    def setXmlValue(self, valuePath, value, replaceMultiple=False) -> bool:
        if value is None:
            print("unable to set {} to {} in {}: {}".format(valuePath, value, self.filename, str(False)))
            return False
        found=False
        pathToFind = XPath(valuePath)
        pattern = re.compile('<([^>^\ ^?^!]+(\ \/)?)')
        curPath=XPath()
        curParent=None
        isComment=False
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
            with open(self.filename) as src_file:
                for line in src_file:
                    if found == False or replaceMultiple:
                        x=line.find('<!--')
                        y=line.find('-->')
                        if x>=0:
                            isComment=True
                        if y>=0 and y > x:
                            isComment=False
                        if not isComment:
                            matches = pattern.finditer(line,y)
                            for matchNum, match in enumerate(matches, 1):
                                f = match.group(1)
                                # end tag detected
                                if f.startswith("/"):
                                    curPath.remove(f[1:])
                                # start tag detected (not autoclosing xml like <br />)
                                elif not f.endswith("/"):
                                    x = curPath.add(f)
                                    if curParent is None:
                                        curParent = x
                                    else:
                                        curParent = curPath.last(1)
                                else:
                                    continue
                                if pathToFind.equals(curPath, False):
                                    pre=line[0:line.index('<')]
                                    line=pre+'<{x}>{v}</{x}>\n'.format(x=f,v=value)
                                    found=True
                                    curPath.remove(f)
                                    break
                                elif pathToFind.parentParamIsNeeded(curPath.subpath(1), f):
                                    v = self.tryToGetValue(line, f)
                                    if v is not None:
                                        curParent.setFilter(f, v)

                    tmp_file.write(line)
            # Overwrite the original file with the munged temporary file in a
            # manner preserving file attributes (e.g., permissions).
            shutil.copystat(self.filename, tmp_file.name)
            shutil.move(tmp_file.name, self.filename)
        print("set {} to {} in {}: {}".format(valuePath, value, self.filename, str(found)))
        return found

    def tryToGetValue(self, line, xmlTag=None):
        pattern = re.compile('<([^>^\ ^?^!]+)>([^<]+)<\/([^>^\ ^?^!]+)>' if xmlTag is None else '<('+xmlTag+')>([^<]+)<\/('+xmlTag+')>') 
        matches = pattern.finditer(line)
        match = next(matches)
        if match is not None:
            return match.group(2)
        return None

    @staticmethod
    def findAll(folder, excludes=[]):
        files= glob.glob(folder + "/**/pom.xml", recursive = True)
        r=[]
        for file in files:
            doExclude=False
            for exclude in excludes:
                if exclude in file:
                    doExclude=True
                    break
            if not doExclude:
                r.append(file)
        return r
