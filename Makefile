# Any test subset can be run by calling make with an appropriate stem,
# e.g. test_int will run test_integration_options_dict_array_nodes.py,
# test_integration_options_dict_misc.py, etc.

default: test

clean:
	rm *.pyc -f
	rm *~ -f

t%: clean
	cd test && $(MAKE) $@
