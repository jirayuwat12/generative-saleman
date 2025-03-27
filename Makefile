format-all:
	isort .
	black .

test:
	pytest
