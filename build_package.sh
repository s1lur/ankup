mkdir -p RPM/{RPMS,SPECS,SOURCES}

mkdir backend/wheels
pip3 wheel --wheel-dir=./backend/wheels -r ./backend/requirements.txt

tar --transform 's,^backend,ankup-1.0.0,' --exclude='Dockerfile' --exclude='requirements.txt' -czf ankup-1.0.0.tar.gz backend/

cp specs/*.spec RPM/SPECS/
cp services/*.service RPM/SOURCES/
cp ankup-1.0.0.tar.gz RPM/SOURCES/

rpmbuild -bb RPM/SPECS/ankup.spec
