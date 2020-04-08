## !!!!! PLEASE READ !!!!!

The actual parent poms are being generated from below two pom-template

##### ODL related parent poms:
ccsdk/parent/odlparent/setup/src/main/template/pom-template.xml

##### Springboot related parent poms:
ccsdk/parent/springboot/spring-boot-setup/src/main/template/pom-template.xml
        
#### Note:
Any updates needed should be made to respective template and not to the generated pom.xml file/files.

Every parent pom has associated properties files (src/main/properties).<br>
Setup module will read those properties and populate respective values within generated pom.xml


