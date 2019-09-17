#! /bin/bash

if [ $# -ne 1 ]
then
	echo "Usage: $0 new-version"
	exit 1
fi


mvn versions:set versions:update-child-modules versions:commit -B -DnewVersion=$1

base_version=$(echo $1 | cut -d- -f1)
major=$(echo $base_version | cut -d. -f1)
minor=$(echo $base_version | cut -d. -f2)
patch=$(echo $base_version | cut -d. -f3)

if [ -f version.properties ]
then
    sed -i ''  -e 's/\(release_name=\).*/\1'$major'/;s/\(sprint_number=\).*/\1'$minor'/;s/\(feature_revision=\).*/\1'$patch'/'  version.properties
fi
