from django.apps import AppConfig
from django.core.checks import Error, register


@register()
def check_icons_library_registered(app_configs, **kwargs):
    """
    The whole site's icon system depends on apps/core/templatetags/icons.py
    being importable. Django's template-library scanner silently swallows
    ImportError when discovering templatetags modules, which turns a
    missing/broken file into a crash on the *first page request* instead
    of an obvious error at startup or in `manage.py check`. This check
    makes that failure loud and immediate instead.
    """
    errors = []
    try:
        from django.template.backends.django import get_installed_libraries
        libraries = get_installed_libraries()
        if 'icons' not in libraries:
            errors.append(Error(
                "The 'icons' template tag library is not registered. "
                "Every page that uses {% load icons %} will crash with "
                "'icons is not a registered tag library' as soon as it's "
                "requested. Most likely apps/core/templatetags/icons.py "
                "is missing from this deployment, or it fails to import "
                "(check for a syntax/import error in that file).",
                id='core.E001',
            ))
    except Exception as e:
        errors.append(Error(
            f"Could not verify the icons template library: {e}",
            id='core.E002',
        ))
    return errors


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
