.PHONY: test

define header
@echo
@printf '%70s\n' | tr ' ' =
@echo " $1"
@printf '%70s\n' | tr ' ' =
@echo
endef

test:
	$(call header,"unit tests")
	cd unittest && $(MAKE)
	$(call header,"functional tests")
	cd functest && $(MAKE)