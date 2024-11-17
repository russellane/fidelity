include Python.mk
PROJECT = fidelity
COV_FAIL_UNDER = 97
lint :: mypy
doc :: README.md

# The following is for manual testing.
FIDELITY := python -m fidelity --use-datafiles
report:
	$(FIDELITY)
