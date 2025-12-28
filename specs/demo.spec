Name:           demo
Version:        1.0.0
Release:        alt1
Summary:        Dummy package for security demo
License:        GPL
Group:          System/Configuration
BuildArch:      noarch
Source0:        demo.sh
Source1:        demo.service

%description
This is a test package to demonstrate digital signature verification.

%prep

%build

%install
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/lib/systemd/system

install -m 755 %{SOURCE0} %{buildroot}/usr/bin/demo-logger.sh

install -m 644 %{SOURCE1} %{buildroot}/lib/systemd/system/demo-logger.service

%post
systemctl daemon-reload

%files
/usr/bin/demo.sh
/lib/systemd/system/demo.service