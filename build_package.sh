set -x

mkdir -p ~/RPM/{RPMS,SPECS,SOURCES}

tar --transform 's,^backend,ankup-1.0.10,' --exclude='Dockerfile' -czf ankup-1.0.10.tar.gz backend/

cp specs/*.spec ~/RPM/SPECS/
cp services/*.service ~/RPM/SOURCES/
cp 'ankup-1.0.10.tar.gz' ~/RPM/SOURCES/

rpmbuild --sign -bb ~/RPM/SPECS/ankup.spec
