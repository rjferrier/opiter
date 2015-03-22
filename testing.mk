test: clean
	@echo
	@printf '%70s\n' | tr ' ' =
	@echo " $(TESTINGSTAGE)"
	@printf '%70s\n' | tr ' ' =
	@echo
	python -m unittest discover .
	@printf '%70s\n' | tr ' ' =
	@echo

clean:
	rm *.pyc -f
	rm *~ -f
