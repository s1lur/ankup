Name:           ankup
Version:        1.0.0
Release:        alt1
Summary:        Django Backend + Celery (Offline Install)
License:        Proprietary
Group:          Networking/Other
BuildArch:      noarch
Url:            http://internal.repo
AutoReqProv:    no

Source0:        %{name}-%{version}.tar.gz

Source1:        ankup-core.service
Source2:        ankup-celery.service
Source3:        ankup-celery-beat.service

Requires:       python3

%set_verify_elf_method skip

%description
Monolithic package containing Django Backend, Celery Worker, and Celery Beat.
Includes all Python dependencies as wheels for offline installation.

%prep
%setup -q

%build

%install
mkdir -p %{buildroot}/opt/%{name}
mkdir -p %{buildroot}/lib/systemd/system
mkdir -p %{buildroot}/var/log/%{name}
mkdir -p %{buildroot}/var/lib/%{name}  # Для расписания celery beat
mkdir -p %{buildroot}/etc/sysconfig

cp -r ./* %{buildroot}/opt/%{name}/

install -m 644 %{SOURCE1} %{buildroot}/lib/systemd/system/ankup-core.service
install -m 644 %{SOURCE2} %{buildroot}/lib/systemd/system/ankup-celery.service
install -m 644 %{SOURCE3} %{buildroot}/lib/systemd/system/ankup-celery-beat.service

touch %{buildroot}/etc/sysconfig/%{name}


%pre
getent passwd ankup_user >/dev/null || \
    useradd -r -s /sbin/nologin -d /opt/%{name} -c "Ankup Service User" ankup_user
exit 0

%post
systemctl daemon-reload

if [ ! -d "/opt/%{name}/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv /opt/%{name}/venv
fi

echo "Installing dependencies from local wheelhouse..."

a= /opt/%{name}/venv/bin/pip install --no-index --find-links=/opt/%{name}/wheels --upgrade pip setuptools wheel

a= /opt/%{name}/venv/bin/pip install --no-index --find-links=/opt/%{name}/wheels -r /opt/%{name}/requirements.txt

chown -R ankup_user:ankup_user /opt/%{name}
chown -R ankup_user:ankup_user /var/log/%{name}
chown -R ankup_user:ankup_user /var/lib/%{name}

if [ $1 -gt 1 ]; then
    echo "Upgrade detected. Restarting services..."
    systemctl try-restart ankup-core
    systemctl try-restart ankup-celery
    systemctl try-restart ankup-celery-beat
fi

%preun
if [ $1 -eq 0 ]; then
    systemctl stop ankup-core ankup-celery ankup-celery-beat
    systemctl disable ankup-core ankup-celery ankup-celery-beat
fi

%postun
systemctl daemon-reload


%files
%defattr(-,root,root,-)

/opt/%{name}

/lib/systemd/system/ankup-core.service
/lib/systemd/system/ankup-celery.service
/lib/systemd/system/ankup-celery-beat.service

%attr(0755, ankup_user, ankup_user) /var/log/%{name}
%attr(0755, ankup_user, ankup_user) /var/lib/%{name}

%config(noreplace) /etc/sysconfig/%{name}
