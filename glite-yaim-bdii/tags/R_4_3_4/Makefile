NAME= $(shell grep Name: *.spec | sed 's/^[^:]*:[^a-zA-Z]*//' )
VERSION= $(shell grep Version: *.spec | sed 's/^[^:]*:[^0-9]*//' )
RELEASE= $(shell grep Release: *.spec |cut -d"%" -f1 |sed 's/^[^:]*:[^0-9]*//')
build=$(shell pwd)/build
DATE=$(shell date "+%a, %d %b %Y %T %z")

default: 
	@echo "Nothing to do"

install:
	@echo installing ...
	@mkdir -p $(prefix)/yaim/functions
	@mkdir -p $(prefix)/yaim/node-info.d
	@mkdir -p $(prefix)/yaim/examples
	@mkdir -p $(prefix)/yaim/examples/siteinfo
	@mkdir -p $(prefix)/yaim/examples/siteinfo/services
	@mkdir -p $(prefix)/yaim/defaults
	@mkdir -p $(prefix)/yaim/etc/versions
	@echo "$(NAME) $(VERSION)-$(RELEASE)" > $(prefix)/yaim/etc/versions/$(NAME)

	@install -m 0644 config/functions/config_* $(prefix)/yaim/functions
	@install -m 0644 config/node-info.d/glite-* $(prefix)/yaim/node-info.d
	@install -m 0644 config/node-info.d/emi-* $(prefix)/yaim/node-info.d
	@install -m 0644 config/defaults/*.pre $(prefix)/yaim/defaults
	@install -m 0644 config/services/glite* $(prefix)/yaim/examples/siteinfo/services/.

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
	rm -rf $(build) rpmbuild

.PHONY: dist srpm rpm sources clean 