init:
	pip install -r requirements.txt

test:
	nosetests tests
envne:
	python3 -m venv env