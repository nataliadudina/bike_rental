from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """ Админ-панель для управления пользователем. """
    fields = ('email', 'password', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_superuser')
    list_display = ('pk', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_display_links = ('email',)
    search_fields = ('last_name', 'email')
    list_filter = ('is_staff', 'is_active')
    ordering = ('pk',)
    list_per_page = 10
