Name: pfsense-2.x-tools
Summary: Scripts used to interact with pfSense2.x remotely
Version: 1.0
Release: 1
Source: pfsense-2.x-tools.tgz
Group: XOpen/Custom
BuildArch: noarch
ExclusiveArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot
License: GPL

%description

Scripts used to interacat with pfSense2.x remotely.
There are two main scripts for now:
1. pfsense-backup.py 
2. pfsense-updateCRL.py

%prep

%setup -q -n pfsense-2.x-tools

%install

pwd
ls
rm -rf %{buildroot}

mkdir -p %{buildroot}/opt/pfsense2.x/bin
mkdir -p %{buildroot}/opt/pfsense2.x/etc
mkdir -p %{buildroot}/opt/pfsense2.x/share

cp -Rv *.py %{buildroot}/opt/pfsense2.x/bin
cp -Rv exampleConfig.ini %{buildroot}/opt/pfsense2.x/share
cp -Rv README.md %{buildroot}/opt/pfsense2.x/share

%post 

%preun

%clean

rm -rf %{buildroot}

%files
%defattr(0644, root, root)

%attr(0755, root, root)/opt/pfsense2.x/bin/*
/opt/pfsense2.x/etc/
/opt/pfsense2.x/share/*

%changelog
* Thu Jun 2 2016 Initial release <stanley.zhang@ityin.net>
- Initail Release
