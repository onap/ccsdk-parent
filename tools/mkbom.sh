#!/bin/bash

if [ $# -ne 3 ]
then
  echo "Usage: $0 groupId artifactId version"
  exit 1
fi

pomGroupId=$1
pomArtifactId=$2
pomVersion=$3

cat <<END
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>$pomGroupId</groupId>
    <artifactId>$pomArtifactId</artifactId>
    <version>$pomVersion</version>
    <packaging>pom</packaging>

    <distributionManagement>
        <repository>
            <id>ecomp-releases</id>
            <url>https://nexus.onap.org/content/repositories/releases</url>
        </repository>
        <snapshotRepository>
            <id>ecomp-snapshots</id>
            <url>https://nexus.onap.org/content/repositories/snapshots</url>
        </snapshotRepository>
    </distributionManagement>

    <dependencyManagement>
        <dependencies>
END


for jar in $(find . -name '*.jar' -print | cut -d'/' -f2- | sort)
do
    version=$(echo $jar | rev | cut -d'/' -f2 | rev)
    artifactId=$(echo $jar | rev | cut -d'/' -f3 | rev)
    groupId=$(echo $jar | rev | cut -d'/' -f4- | rev | tr '/' '.')


    echo "        <dependency>"
    echo "            <groupId>$groupId</groupId>"
    echo "            <artifactId>$artifactId</artifactId>"
    echo "            <version>$version</version>"
    echo "        </dependency>"
done

cat  <<END
        </dependencies>
    </dependencyManagement>
</project>
END
