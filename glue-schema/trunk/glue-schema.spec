Name:           glue-schema
Version:        2.0.1
Release:        1%{?dist}
Summary:        LDAP schema file for the GLUE Schema version 2.
Group:          Applications/Databases
License:        
URL:            http://forge.gridforum.org/sf/projects/glue-wg
Source0:        http://glue.web.cern.ch/glue/glue-schema-%{version}.src.tgz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
LDAP schema file for the GLUE Schema version 2.0

%prep
%setup -q

%build
%configure

%install
rm -rf $RPM_BUILD_ROOT
make -f INSTALL install prefix=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
/etc/ldap/schema/

%changelog
