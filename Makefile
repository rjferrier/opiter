default: test

clean:
	rm *.pyc -f
	rm *~ -f

%: clean
	cd test && $(MAKE) $@
