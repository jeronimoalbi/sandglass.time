# pylint: disable=C0103

from pyramid.security import NO_PERMISSION_REQUIRED

# Short alias for permission rules that are public
PUBLIC = NO_PERMISSION_REQUIRED

# Group definition for administrators
Administrators = "time.Administrators"
