from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from account.models import UserAccount
# Register your models here.


class AccountAdmin(UserAdmin):
    # Column fields to display
    list_display = ('email', 'username', 'date_joined',
                    'last_login', 'is_admin', 'is_staff')
    # What can be searched for in the search field
    search_fields = ('email', 'username')
    # Readonly fields in the model
    readonly_fields = ('id', 'date_joined', 'last_login')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(UserAccount, AccountAdmin)
