Name:		glite-info-update-endpoints
Version:	2.0.9
Release:	1%{?dist}
Summary:	Updates LDAP endpoins for EGI and OSG
Group:		System/Monitoring
License:	ASL 2.0
Source:		%{name}-%{version}.src.tgz
BuildArch:	noarch
BuildRoot:	%{_tmppath}/%{name}-%{version}-build

%description
Updates LDAP endpoins for EGI and OSG

%prep
%setup -q

%build
# Nothing to build

%install
rm -rf %{buildroot}
make install prefix=%{buildroot}

%post
if [ ! -f /opt/glite/etc/gip/top-urls.conf ]; then
    /etc/cron.hourly/glite-info-update-endpoints
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%dir /etc/glite/
%dir /opt/glite/etc/gip
%dir /var/log/glite/
%dir /var/cache/glite/
%config(noreplace) /etc/glite/glite-info-update-endpoints.conf
/usr/bin/glite-info-update-endpoints
/etc/cron.hourly/glite-info-update-endpoints
/var/cache/glite/glite-info-update-endpoints
%changelog
* Mon Apr 19 2012 Laurence Field <laurence.field@cern.ch> - 2.0.9-1
- Added random sleep to cronjob to address GGUS #81404 
* Mon Mar 28 2011 Laurence Field <laurence.field@cern.ch> - 2.0.8-1
- Addressed IS-228
* Fri Aug 20 2010 Laurence Field <laurence.field@cern.ch> - 2.0.3-1
- Refactored version that queries the GOCs directly
