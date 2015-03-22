.PHONY: default

default: test

%:
	cd optree   && $(MAKE) $@
	cd unittest && $(MAKE) $@
	cd inttest  && $(MAKE) $@
	cd functest && $(MAKE) $@
