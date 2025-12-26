Name:           demo
Version:        1.0.0
Release:        alt1
Summary:        Dummy package for security demo
License:        GPL
Group:          System/Configuration
BuildArch:      noarch

%description
This is a test package to demonstrate digital signature verification.

%prep

%build

%install
mkdir -p %{buildroot}/etc
echo "Hello from signed package!" > %{buildroot}/etc/hello_world.conf

%files
/etc/hello_world.conf
