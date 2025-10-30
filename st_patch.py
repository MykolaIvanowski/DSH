# st_patch.py
import sys
from django.utils.module_loading import import_string
import importlib
import django.contrib.staticfiles.storage as sfs_mod
from django.conf import settings

print("ST_PATCH: running", file=sys.stderr)
print("ST_PATCH: STATICFILES_STORAGE =", settings.STATICFILES_STORAGE, file=sys.stderr)

# ensure we replace whatever instance may have been created earlier
try:
    sfs_mod.staticfiles_storage = import_string(settings.STATICFILES_STORAGE)()
    print("ST_PATCH: reassigned staticfiles_storage to", sfs_mod.staticfiles_storage.__class__, file=sys.stderr)
except Exception as e:
    print("ST_PATCH: FAILED to reassign staticfiles_storage:", repr(e), file=sys.stderr)