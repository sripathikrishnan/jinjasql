import sys

if sys.version_info >= (2, 7) and sys.version_info <= (3, 4):

    from django.test import TestCase, RequestFactory
    from jinjasql import JinjaSql

    import unittest

    @unittest.skipIf(sys.version_info < (2, 7), 
        "django version not supported in python 2.6.x")
    class DjangoTest(TestCase):
        def test_django_request_as_context(self):
            request = RequestFactory().get('/customer/details/?customer=1232&enterprise=9875')
            j = JinjaSql()
            query, bind_params = j.prepare_query("""select {{request.path}} 
                from dual 
                where customer={{request.GET.customer}}"""
                , {"request": request}
            )
            self.assertEquals(bind_params, [u"/customer/details/", u"1232"])


    def configure_django():
        from django.conf import settings
        import django

        settings.configure(
            DEBUG_PROPAGATE_EXCEPTIONS=True,
            DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3',
                                   'NAME': ':memory:'}},
            SITE_ID=1,
            SECRET_KEY='not very secret in tests',
            USE_I18N=True,
            USE_L10N=True,
            STATIC_URL='/static/',
            ROOT_URLCONF='tests.urls',
            TEMPLATE_LOADERS=(
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ),
            MIDDLEWARE_CLASSES=(
                'django.middleware.common.CommonMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
            ),
            INSTALLED_APPS=(
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.sites',
                'django.contrib.messages',
                'django.contrib.staticfiles',
            ),
            PASSWORD_HASHERS=(
                'django.contrib.auth.hashers.SHA1PasswordHasher',
                'django.contrib.auth.hashers.PBKDF2PasswordHasher',
                'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
                'django.contrib.auth.hashers.BCryptPasswordHasher',
                'django.contrib.auth.hashers.MD5PasswordHasher',
                'django.contrib.auth.hashers.CryptPasswordHasher',
            ),
        )
        django.setup()

    configure_django()
