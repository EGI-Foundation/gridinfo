Name:		ginfo
Version:	0.1.5
Release:	1%{?dist}
Summary:	Service Discovery Client

Group:		Applications/Internet
License:	ASL 2.0
URL:		https://svnweb.cern.ch/trac/gridinfo/browser/ginfo
# The source for this package was pulled from upstream's vcs.  Use the
# following commands to generate the tarball:
#   svn export http://svnweb.cern.ch/guest/gridinfo/ginfo/tags/R_0_1_5 %{name}-%{version}
#  tar --gzip -czvf %{name}-%{version}.tar.gz %{name}-%{version} 

Source:		%{name}-%{version}.tar.gz
BuildArch:	noarch
BuildRoot:	%{_tmppath}/%{name}-%{version}-build

Requires:      python-ldap
%if "%{?dist}" == ".el5"
Requires:      python-json
%endif

%description
Service Discovery Client for obtaining GLUE 2.0 information on Grid services. 

%prep
%setup -q

%build

%install
rm -rf %{buildroot}
make install prefix=%{buildroot}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{_bindir}/ginfo
%{_mandir}/man1/ginfo.1*
%doc LICENSE

%changelog
* Tue Jun 19 2012 Laurence Field <laurence.field@cern.ch> - 0.1.5-1
- Initial version
