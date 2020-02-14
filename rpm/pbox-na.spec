############################
# Scep file for Personal Box Node Agent
############################

Summary: Node Agent for Personal Box
Name: pbox-na
Version: 0.0.16
Release: 1
Requires: python3
Requires: python3-requests
Requires: python3-flask
Requires: sqlite
License: FIXME
Source0: https://github.com/Ben-Banso/pbox-na/archive/master.zip

%description
API to make the server part of a shared docker cluster

%prep
wget https://github.com/Ben-Banso/pbox-na/archive/master.zip

exit

%install
mkdir -p $RPM_BUILD_ROOT/etc/pbox-na
mkdir -p $RPM_BUILD_ROOT/usr/sbin
mkdir -p $RPM_BUILD_ROOT/lib/systemd/system
cp pbox-na-master/pbox-na.py $RPM_BUILD_ROOT/usr/sbin/pbox-na.py

%files
/etc/pbox-na/settings.conf
/etc/pbox-na/version.txt
/usr/sbin/pbox-na.py
/lib/systemd/system/pbox-na.service


%post
systemctl daemon-reload

exit
