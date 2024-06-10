from django.contrib import admin
from foodapp.models import Food, Cust, Admin, Cart, Order
from .models import Food
class FoodAdmin(admin.ModelAdmin):
     list_display = ('FoodName', 'FoodPrice', 'Description')
     list_filter = ('FoodPrice',)
# Register the models with the admin site
admin.site.register(Food, FoodAdmin)
admin.site.register(Cust)
admin.site.register(Admin)
admin.site.register(Cart)
admin.site.register(Order)
