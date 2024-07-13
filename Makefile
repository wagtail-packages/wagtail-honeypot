run:
	python manage.py runserver 0:8000

mail:
	docker run -p 8025:8025 -p 1025:1025 mailhog/mailhog

test:
	coverage run manage.py test && coverage report

tox:
	tox --skip-missing-interpreters

migrate:
	python manage.py migrate

superuser:
	@echo "from django.contrib.auth import get_user_model; get_user_model().objects.create_superuser('admin', 'admin@admin.com', 'changeme')" | python manage.py shell
