Name:           demo-bad-sig
Version:        1.0.0
Release:        alt1
Summary:        Dummy package for security demo (should have corrupted signature)
License:        GPL
Group:          System/Configuration
BuildArch:      noarch

%description
This is a test package to demonstrate digital signature verification.

%prep

%build

%install
mkdir -p %{buildroot}/etc
echo "Hello from corrupted package!" > %{buildroot}/etc/hello_bad_sig.conf

%files
/etc/hello_bad_sig.conf
