Name:           demo-bad-hash
Version:        1.0.0
Release:        alt1
Summary:        Dummy package for security demo (should have corrupted hash)
License:        GPL
Group:          System/Configuration
BuildArch:      noarch

%description
This is a test package to demonstrate hashsum verification.

%prep

%build

%install
mkdir -p %{buildroot}/etc
echo "Hello from corrupted package!" > %{buildroot}/etc/hello_bad_hash.conf

%files
/etc/hello_bad_hash.conf
