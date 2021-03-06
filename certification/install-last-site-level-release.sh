#!/bin/bash

repo='http://grid-deployment.web.cern.ch/grid-deployment/glite/repos/3.2/glite-BDII_site.repo'
wget ${repo} -O /etc/yum.repos.d/glite-BDII_site.repo 
yum install -y glite-BDII_site

MY_DOMAIN=$(hostname -d)
MY_HOST=$(hostname -f)

# Create site-info.def
cat <<EOF > /root/site-info.def 

# Site Information
SITE_NAME=TestSite
SITE_EMAIL="email@${MY_DOMAIN}"
SITE_LAT=1.0 
SITE_LONG=1.0
SITE_DESC="Test Site"
SITE_LOC="Place, Country"
SITE_WEB="http://${MY_DOMAIN}"
SITE_SECURITY_EMAIL="security@${MY_DOMAIN}"
SITE_SUPPORT_EMAIL="support@${MY_DOMAIN}"
SITE_OTHER_GRID="MYGrid"


SITE_BDII_HOST=${MY_HOST}

BDII_REGIONS="SITE_BDII"
BDII_SITE_BDII_URL="ldap://${MY_HOST}:2170/mds-vo-name=resource,o=grid"

EOF
    
/opt/glite/yaim/bin/yaim -c -s /root/site-info.def -n BDII_site 
