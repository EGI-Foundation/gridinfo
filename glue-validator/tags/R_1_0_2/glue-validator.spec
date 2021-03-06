%if 0%{?rhel} <= 5
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%endif
Summary: A validation framework for Grid information providers
Name: glue-validator
Version: 1.0.2
Release: 1%{?dist}
# The source for this package was pulled from upstream's vcs.  Use the
# following commands to generate the tarball:
#   svn export http://svnweb.cern.ch/guest/gridinfo/glue-validator/tags/R_1_0_2 %{name}-%{version}
#  tar -czvf %{name}-%{version}.tar.gz %{name}-%{version}
Source0: %{name}-%{version}.tar.gz
License: ASL 2.0
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-buildroot
BuildArch: noarch
BuildRequires: python-devel
Requires: openldap-clients
Url: http://cern.ch/glue

%description
A validation framework for Grid information providers. 
This framework validates the information return against the GLUE information 
model from the Open Grid Forum. 

%prep
%setup -q

%build
%{__python} setup.py build

%install
rm -rf %{buildroot}
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT 
mkdir -p %{buildroot}/usr/share/man/man1
install -m 0644 man/glue-validator.1 %{buildroot}/usr/share/man/man1
%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc LICENSE
%{python_sitelib}/*
%{_bindir}/glue-validator
%{_mandir}/man1/glue-validator.1.gz

%changelog
* Wed Dec 14 2011 Laurence Field <laurence.field@cern.ch>  - 1.0.2-1
- New upstream version and packaging improvements
* Mon Dec 05 2011 Laurence Field <laurence.field@cern.ch>  - 1.0.1-1
- New upstream version and packaging improvements
* Fri Nov 11 2011 Laurence Field <laurence.field@cern.ch>  - 1.0.0-1
- Initial Release
