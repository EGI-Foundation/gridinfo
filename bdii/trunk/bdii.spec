%define metadata CONFIG
%define name %( grep NAME %{metadata} | sed 's/^[^=]*=//' )
%define version %( grep VERSION %{metadata} | sed 's/^[^=]*=//' )
%define release %( grep RELEASE %{metadata} | sed 's/^[^=]*=//' )
%define prefix %( grep PREFIX %{metadata} | sed 's/^[^=]*=//' )
%define license %( grep LICENSE %{metadata} | sed 's/^[^=]*=//' )
%define vendor %( grep VENDOR %{metadata} | sed 's/^[^=]*=//' )
%define packager %( grep PACKAGER %{metadata} | sed 's/^[^=]*=//' )
%define group %( grep GROUP %{metadata} | sed 's/^[^=]*=//' )
%define desc %( grep DESCRIPTION %{metadata} | sed 's/^[^=]*=//' )

Summary: %{name}
Name: %{name}
Version: %{version}
Vendor: %{vendor}
Release: %{release}
License: %{license}
Group: %{group}
Source: %{name}-%{version}.src.tgz
BuildArch: noarch
Prefix: %{prefix}
BuildRoot: %{_tmppath}/%{name}-%{version}-build
Packager: %{packager}
Requires: openldap-clients
Requires: openldap-servers
Requires: expect
Requires: lsb
Requires: glue-schema >= 2.0.0

%description
%{desc}

%prep

%setup -c

%build
make -f INSTALL install prefix=%{buildroot}%{prefix}

%pre
if [ -f /opt/bdii/sbin/bdii-update ]; then
    /etc/rc.d/init.d/bdii stop
fi

%post
sed -i  "s/.*rootpw.*secret.*/rootpw    $(/usr/bin/mkpasswd -s 0)/" /opt/bdii/etc/bdii-slapd.conf
chkconfig --add bdii 
/etc/init.d/bdii condrestart || true

%preun
if [ $1 -eq 0 ]; then
    /etc/init.d/bdii stop || true
    /sbin/chkconfig --del bdii
fi

%files 
%defattr(-,root,root)
%attr(0755,ldap,ldap) %dir /opt/bdii
%attr(0755,ldap,ldap) %dir /var/bdii/
%attr(0755,ldap,ldap) %dir /var/bdii/db
%attr(0755,ldap,ldap) %dir /var/bdii/db/stats
%attr(0755,ldap,ldap) %dir /var/bdii/db/glue2
%attr(0755,ldap,ldap) %dir /var/bdii/archive
%attr(0755,ldap,ldap) %dir /var/log/bdii/
%dir /opt/glite/etc/gip/ldif
%dir /opt/glite/etc/gip/provider
%dir /opt/glite/etc/gip/plugin
%dir /var/lock/subsys
%config(noreplace) /opt/bdii/etc/DB_CONFIG
%config(noreplace) /opt/bdii/etc/bdii.conf
%config(noreplace) /opt/bdii/etc/BDII.schema
%config(noreplace) /opt/bdii/etc/bdii-slapd.conf
%config(noreplace) /opt/glite/etc/gip/ldif/default.ldif
/etc/init.d/bdii
/etc/logrotate.d/bdii
/etc/cron.d/bdii-proxy
/opt/bdii/bin/bdii-update
/opt/bdii/bin/bdii-proxy

%clean
rm -rf %{buildroot}
