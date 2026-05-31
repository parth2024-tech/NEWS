.PHONY: install run-phase-1 run-phase-2 run-phase-3 clean

install:
	pip install -r requirements.txt

run-phase-1:
	python agent.py --phase 1

run-phase-2:
	python agent.py --phase 2

run-phase-3:
	python agent.py --phase 3

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	rm -rf venv/
