#!/bin/bash

updatePom() {
cat $1 | xsltproc -o $1 /tmp/rebase-pom.xslt -
}

export -f updatePom

# Create XSLT script
newVersion=$2
echo "newVersion is $newVersion"
cat <<END > /tmp/rebase-pom.xslt
<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:pom="http://maven.apache.org/POM/4.0.0"
    xmlns="http://maven.apache.org/POM/4.0.0"
    exclude-result-prefixes="pom">
    <xsl:output method="xml" encoding="UTF-8" indent="yes" omit-xml-declaration="no" cdata-section-elements="sdnc.keypass"/>

    <!-- Copy everything that does not match a rewrite rule -->
    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()" />
        </xsl:copy>
    </xsl:template>

    <!-- Change ccsdk parent pom version -->
    <xsl:template match="//pom:parent[pom:groupId='org.onap.ccsdk.parent']/pom:version">
	<version>$newVersion</version>
    </xsl:template>
</xsl:stylesheet>
END

if [ $# -ne 2 ]
then
	echo "Usage: $0 <directory> <version>"
	exit 1
fi

find $1 -name pom.xml -exec bash -c 'updatePom "$0" $1' '{}' \;

#Adding single empty line before project tag if there is a header available
find $1 -name pom.xml -exec sed -i '' '$!N;s@-->\n<project@-->\
\
<project@;P;D' {} \;
