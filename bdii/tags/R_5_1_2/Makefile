NAME= $(shell grep Name: *.spec | sed 's/^[^:]*:[^a-zA-Z]*//' )
VERSION= $(shell grep Version: *.spec | sed 's/^[^:]*:[^0-9]*//' )
RELEASE= $(shell grep Release: *.spec |cut -d"%" -f1 |sed 's/^[^:]*:[^0-9]*//')
build=$(shell pwd)/build
DATE=$(shell date "+%a, %d %b %Y %T %z")

default: 
	@echo "Nothing to do"

install:
	@echo installing ...
	@mkdir -p $(prefix)/usr/sbin/
	@mkdir -p $(prefix)/var/lib/bdii/gip/ldif/
	@mkdir -p $(prefix)/var/lib/bdii/gip/provider/
	@mkdir -p $(prefix)/var/lib/bdii/gip/plugin/
	@mkdir -p $(prefix)/etc/bdii/
	@mkdir -p $(prefix)/etc/init.d/
	@mkdir -p $(prefix)/etc/logrotate.d/
	@mkdir -p $(prefix)/etc/cron.d/
	@mkdir -p $(prefix)/var/log/bdii/
	@mkdir -p $(prefix)/usr/share/doc/bdii/

	@install -m 0755 etc/init.d/bdii      $(prefix)/etc/init.d/
	@install -m 0755 bin/bdii-update      $(prefix)/usr/sbin/
	@install -m 0755 bin/bdii-proxy       $(prefix)/usr/sbin/
	@install -m 0644 etc/bdii.conf	      $(prefix)/etc/bdii/
	@install -m 0644 etc/BDII.schema     $(prefix)/etc/bdii/
	@install -m 0644 etc/bdii-slapd.conf  $(prefix)/etc/bdii/
	@install -m 0644 etc/DB_CONFIG        $(prefix)/etc/bdii/
	@install -m 0644 etc/default.ldif     $(prefix)/var/lib/bdii/gip/ldif/
	@install -m 0644 etc/logrotate.d/bdii $(prefix)/etc/logrotate.d
	@install -m 0644 etc/cron.d/bdii-proxy $(prefix)/etc/cron.d

dist:
	@mkdir -p  $(build)/$(NAME)-$(VERSION)/
	rsync -HaS --exclude ".svn" --exclude "$(build)" * $(build)/$(NAME)-$(VERSION)/
	cd $(build); tar --gzip -cf $(NAME)-$(VERSION).tar.gz $(NAME)-$(VERSION)/; cd -

sources: dist
	cp $(build)/$(NAME)-$(VERSION).tar.gz .

deb: dist
	cd $(build)/$(NAME)-$(VERSION); dpkg-buildpackage -us -uc; cd -

prepare: dist
	@mkdir -p  $(build)/RPMS/noarch
	@mkdir -p  $(build)/SRPMS/
	@mkdir -p  $(build)/SPECS/
	@mkdir -p  $(build)/SOURCES/
	@mkdir -p  $(build)/BUILD/
	cp $(build)/$(NAME)-$(VERSION).tar.gz $(build)/SOURCES 

srpm: prepare
	@rpmbuild -bs --define='_topdir ${build}' $(NAME).spec

rpm: srpm
	@rpmbuild --rebuild  --define='_topdir ${build} ' $(build)/SRPMS/$(NAME)-$(VERSION)-$(RELEASE).src.rpm

clean:
	rm -f *~ $(NAME)-$(VERSION).tar.gz
	rm -rf $(build)

.PHONY: dist srpm rpm sources clean 