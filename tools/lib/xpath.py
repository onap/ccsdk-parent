
import re


class XPathComponent:
    regex = r"([^\/^\[]+)(\[([^\]]+)\])?"
    def __init__(self, expr):
        matches = re.finditer(XPathComponent.regex, expr, re.DOTALL | re.IGNORECASE)
        match = next(matches)
        self.name = match.group(1)
        tmp = match.group(3) if len(match.groups())>2 else None
        self.filter = tmp.split(',') if tmp is not None else [] 

    def equals(self, comp, ignoreFilter=False) -> bool:
        if ignoreFilter:
            return self.name == comp.name
        if self.name == comp.name:
            return set(self.filter) == set(comp.filter)
        return False
    
    def setFilter(self, f, v):
        self.filter.append('{}={}'.format(f,v))

    def hasFilter(self, propertyName):
        search=propertyName+'='
        for filter in self.filter:
            if filter.startswith(search):
                return True
        return False

    def __str__(self) -> str:
        return "XPathComponent[name={}, filter={}]".format(self.name, self.filter)
    
class XPath:

    def __init__(self, expr=None):
        self.raw = expr
        tmp = expr.split('/') if expr is not None else []
        self.components=[]
        if len(tmp)>0 and len(tmp[0])==0:
            tmp.pop(0)
        for x in tmp:
            self.components.append(XPathComponent(x))
    
    def add(self, c: str) -> XPathComponent:
        xc=XPathComponent(c)
        self.components.append(xc)
        return xc

    def remove(self, c: str) -> bool:
        if self.components[len(self.components)-1].equals(XPathComponent(c), True):
            self.components.pop()
            return True
        return False

    def parentParamIsNeeded(self, xp, paramName) -> bool:
        for i in range(len(xp.components)):
            if i>=len(self.components):
                return False
            if not self.components[i].equals(xp.components[i], True):
                return False
        return self.components[len(xp.components)-1].hasFilter(paramName)

    def equals(self, path, ignoreFilter=False) -> bool:
        if len(self.components) != len(path.components):
            return False

        for i in range(len(self.components)):
            if not self.components[i].equals(path.components[i], ignoreFilter):
                return False
        return True

    def lastname(self) -> str:
        tmp = self.last()
        return tmp.name if tmp is not None else ""

    def last(self, off=0) -> XPathComponent:
        return self.components[len(self.components)-1-off] if len(self.components)>off else None

    def subpath(self, off=0):
        tmp =XPath()
        for i in range(len(self.components)-off):
            tmp.components.append(self.components[i])
        return tmp