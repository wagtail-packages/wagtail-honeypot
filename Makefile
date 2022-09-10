run:
	@echo "Running sandbox..."
	python sandbox/manage.py runserver 0:8000

mail:
	@echo "Running sandbox mail..."
	cp sandbox/sandbox/settings/local.py.example.py sandbox/sandbox/settings/local.py
	docker run -p 8025:8025 -p 1025:1025 mailhog/mailhog

test:
	python testmanage.py test

tox:
	tox --skip-missing-interpreters
