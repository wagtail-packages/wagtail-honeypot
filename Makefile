run:
	python manage.py runserver 0:8000

mail:
	docker run -p 8025:8025 -p 1025:1025 mailhog/mailhog

test:
	python manage.py test

tox:
	tox --skip-missing-interpreters

migrate:
	python manage.py migrate

superuser:
	@echo "from django.contrib.auth import get_user_model; get_user_model().objects.create_superuser('admin', 'admin@admin.com', 'admin')" | python manage.py shell

dumpdata:
	python manage.py dumpdata --indent 2 --natural-foreign \
	-e wagtailsearch -e contenttypes -e wagtailcore.pagelogentry -e wagtailcore.groupcollectionpermission \
	-e auth.permission -e wagtailcore.referenceindex -e auth.group -e wagtailcore.workflow \
	-e sessions -e wagtailcore.workflowtask -e wagtailcore.pagesubscription -e wagtailcore.grouppagepermission \
	-e wagtailcore.collection -e wagtailcore.workflowpage -e wagtailcore.task -e wagtailcore.groupapprovaltask \
	-e wagtailredirects.redirect \
	> tests/fixtures/dump.json
