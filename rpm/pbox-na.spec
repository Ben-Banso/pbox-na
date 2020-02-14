############################
# Scep file for Personal Box Node Agent
############################

Summary: Node Agent for Personal Box
Name: pbox-na
Version: 0.1.16
Release: 1
BuildArch: noarch
Requires: python3
Requires: python3-requests
Requires: python3-flask
Requires: sqlite
License: FIXME
Source0: %{name}-%{version}.tar.gz

%description
API to make the server part of a shared docker cluster

%prep
%setup -q

%install
mkdir -p $RPM_BUILD_ROOT/etc/pbox-na
mkdir -p $RPM_BUILD_ROOT/usr/sbin
mkdir -p $RPM_BUILD_ROOT/lib/systemd/system
cp pbox-na.py $RPM_BUILD_ROOT/usr/sbin/
cp version.txt $RPM_BUILD_ROOT/etc/pbox-na/
cp settings.conf $RPM_BUILD_ROOT/etc/pbox-na/
cp rpm/pbox-na.service $RPM_BUILD_ROOT/lib/systemd/system/

%files
/etc/pbox-na/settings.conf
/etc/pbox-na/version.txt
/usr/sbin/pbox-na.py
/lib/systemd/system/pbox-na.service


%post
systemctl daemon-reload

exit
