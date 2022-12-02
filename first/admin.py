from django.contrib import admin


from .models import records, sources, projects, accounts, contragents, accounts_permission 

admin.site.register(records)
admin.site.register(accounts_permission)
admin.site.register(sources)
admin.site.register(projects)
admin.site.register(accounts)
admin.site.register(contragents)

# Register your models here.
