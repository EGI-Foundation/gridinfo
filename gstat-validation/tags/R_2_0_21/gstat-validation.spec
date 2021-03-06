Summary: Gstat Valiation Scripts
Name: gstat-validation
Version: 2.0.21
Release: 1%{?dist}
Source0: %{name}-%{version}.tar.gz
License: EGEE
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-buildroot
Prefix: %{_prefix}
BuildArchitectures: noarch
Vendor: Laurence Field <Laurence.Field@cern.ch>
Requires: openldap-clients
Requires: python-dns
Obsoletes: gstat-core
Url: http://goc.grid.sinica.edu.tw/gocwiki/GSIndex

%description
Valiation scripts for an LDAP based information system using the Glue 1.2 schema

%prep
%setup

%build
python setup.py build

%install
python setup.py install --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
chmod 777 $RPM_BUILD_ROOT/usr/share/gstat/locations
chmod 777 $RPM_BUILD_ROOT/usr/share/gstat/wlcg-tier

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
/usr/share/gstat 


