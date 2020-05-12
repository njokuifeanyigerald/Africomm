from django.urls import path,include
from .views import (
    Home,Checkout,ItemDetailView,add_to_cart,
        remove_from_cart,Ordersummary,remove_single_from_cart,
        PaymentView,AddCoupon,RequestRefundView
    )

app_name="app"
urlpatterns = [
    path('', Home.as_view(), name="home"),
    path('checkout/', Checkout.as_view(), name="checkout"),
    path('products/<slug>/', ItemDetailView.as_view(), name="product"),
    path('payment/<payment_option>/', PaymentView.as_view(), name="PaymentView"),
    path('Ordersummary/', Ordersummary.as_view(), name="Ordersummary"),
    path('add_to_cart/<slug>/',add_to_cart, name="add_to_cart"),
    path('remove_from_cart/<slug>/',remove_from_cart, name="remove_from_cart"),
    path('remove_single_from_cart/<slug>/',remove_single_from_cart, name="remove_single_from_cart"),
    path('AddCoupon/',AddCoupon.as_view(), name="add_coupon"),
     path('Refund/',RequestRefundView.as_view(), name="RequestRefundView"),
    
    
]
