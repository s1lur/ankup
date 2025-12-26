Name:           demo-corrupt-header
Version:        1.0.0
Release:        alt1
Summary:        Dummy package for security demo (should be corrupted)
License:        GPL
Group:          System/Configuration
BuildArch:      noarch

%description
This is a test package to demonstrate digital signature verification.

%prep

%build

%install
mkdir -p %{buildroot}/etc
echo "Hello from corrupted package!" > %{buildroot}/etc/hello_world_corr.conf

%files
/etc/hello_world_corr.conf
