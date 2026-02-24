include Python.mk
PROJECT = fidelity
lint :: mypy
doc :: README.md

# The following is for manual testing.
FIDELITY := pdm run python -m fidelity --use-datafiles
report:
	$(FIDELITY)
