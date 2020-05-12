from django.contrib import admin
from .models import OrderItem,Order,Item,BillingModel,Payment, Coupon

def makeRefundAccepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False,refund_granted=True )
makeRefundAccepted.short_description = 'update orders to refund granted'

class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "user", "ordered", "being_delivered",
     "received" ,"refund_requested", "refund_granted","billing_address","shipping_address", "payment", "coupon"
     ]
    list_filter = ["user", "ordered", "being_delivered", "received" ,"refund_requested", "refund_granted"]
    list_display_links =["user", "billing_address","shipping_address", "payment", "coupon" ]
    search_fields = ['user__username', 'ref_code']

    actions =[makeRefundAccepted]
class BillingModelAdmin(admin.ModelAdmin):
    list_display = ['user','street_address','apartment', 'billingzip','addressType','default', 'date']                   
                    
                    
    list_filter = ['default', 'addressType','country']
    search_fields = ['user__username', 'street_address','addressType','billingzip']
    

admin.site.register(OrderItem)
admin.site.register(Order,OrderAdmin)
admin.site.register(Item)
admin.site.register(BillingModel,BillingModelAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)