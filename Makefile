export PYTHONPATH=$(CURDIR)
export PYTHON=python

# Any test subset can be run by calling make with an appropriate stem,
# e.g. test_int will run test_integration_array_node_info.py,
# test_integration_options_array.py, etc.

default: test

all: clean test

clean:
	rm *.pyc -f
	rm *~ -f
	cd test && $(MAKE) $@

examples/%:
	python $@.py

t%: clean
	cd test && $(MAKE) $@
