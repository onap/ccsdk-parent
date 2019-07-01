#!/usr/bin/env bash

updatePom() {
export XMLLINT_INDENT="    "
cat $1 | xsltproc -o $1 /tmp/rebase-pom.xslt -
}

export -f updatePom

# Copy blueprints to new directory structure
find . -path '*/src/main/resources/org/opendaylight/blueprint/*.xml' -execdir sh -c "mkdir -p ../../../OSGI-INF/blueprint; cp {} ../../../OSGI-INF/blueprint" \;

# Update ietf-net-types dependencies

cat <<END > /tmp/rebase-pom.xslt
<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:pom="http://maven.apache.org/POM/4.0.0"
    xmlns="http://maven.apache.org/POM/4.0.0"
    exclude-result-prefixes="pom">
    <xsl:output method="xml" encoding="UTF-8" indent="yes" omit-xml-declaration="no"/>

    <!-- Copy everything that does not match a rewrite rule -->
    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()" />
        </xsl:copy>
    </xsl:template>

    <xsl:template match="//pom:dependency[pom:groupId='org.opendaylight.mdsal.model' and pom:artifactId='ietf-inet-types-2013-07-15']">
    <dependency>
        <groupId>org.opendaylight.mdsal.binding.model.ietf</groupId>
        <artifactId>rfc6991</artifactId>
	</dependency>
    </xsl:template>

    <xsl:template match="//pom:dependency[pom:groupId='org.opendaylight.mdsal.model' and pom:artifactId='ietf-yang-types-20130715']">
    </xsl:template>
</xsl:stylesheet>
END

find . -name pom.xml -exec bash -c 'updatePom "$0" .' '{}' \;
