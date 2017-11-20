all:
	@echo "Usage:\n"
	@echo "\treset: reset every test value\n"
	@echo "\trun: run every test\n"
	@echo "\tclean: remove every test directory\n"

reset:
	for suite in *; do if [ -d $$suite ] ; then $(MAKE) -C $$suite ; fi ; done;

clean:
	for suite in *; do $(MAKE) clean -C $$suite; done

run:
	for suite in *; do if [ -d $$suite ] ; then $(MAKE) run -C $$suite ; fi ; done

