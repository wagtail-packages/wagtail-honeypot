EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "0.0.0.0"
EMAIL_PORT = 1025
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = False

DEFAULT_FROM_EMAIL = "foo@localhost"

WAGTAIL_QR_CODE_BASE_URL = "http://localhost:8000"

# honeypot default settings
HONEYPOT_NAME = "whf_name"
HONEYPOT_TIME = "whf_time"
HONEYPOT_INTERVAL = 3  # minimum time taken to fill out the form in seconds
