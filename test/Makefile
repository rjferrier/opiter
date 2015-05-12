define run
@echo
@printf '%70s\n' | tr ' ' =
@echo ' Running $1*.py'
@printf '%70s\n' | tr ' ' =
@echo
python -m unittest discover -p '$1*.py'
@printf '%70s\n' | tr ' ' =
@echo
endef

default: test

clean:
	rm *.pyc -f
	rm *~ -f

test%: clean
	$(call run,${@:%.o=%})
