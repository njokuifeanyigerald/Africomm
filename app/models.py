from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django_countries.fields import CountryField


User = get_user_model()

CATEGORY_CHOICES = (
    ('S', 'Shirt'),
    ('SW', 'Sport Wear'),
    ('OW', 'Outwear'),
    
)
Label_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger'),
    
)
ADDRESS_CHOICES = (
    ('B', 'billing'),
    ('S', 'shipping'),
    
    
)

class  Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True,null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=4)
    label = models.CharField(choices=Label_CHOICES, max_length=1)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("app:product", kwargs={
            "slug": self.slug
        })
    def get_add_to_cart(self):
        return reverse("app:add_to_cart", kwargs={
            "slug": self.slug
        })
    def remove_from_cart(self):
        return reverse("app:remove_from_cart", kwargs={
            "slug": self.slug
        })

class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    ordered= models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price
    def get_total_discount_price(self):
        return self.quantity * self.item.discount_price
    def getAmountSaved(self):
        return self.get_total_item_price() - self.get_total_discount_price()
    def getFinalPrice(self):
        if self.item.discount_price:
            return self.get_total_discount_price()
        return self.get_total_item_price()
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date= models.DateTimeField(auto_now_add=True)
    ordered_date= models.DateTimeField()
    ordered= models.BooleanField(default=False)
    billing_address = models.ForeignKey('BillingModel', related_name="billing_address" ,on_delete=models.SET_NULL, null=True, blank=True)
    shipping_address = models.ForeignKey('BillingModel', related_name="shipping_address",on_delete=models.SET_NULL, null=True, blank=True)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, null=True, blank=True)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, null=True, blank=True)
    ref_code= models.CharField(max_length=20)
    being_delivered= models.BooleanField(default=False)
    received= models.BooleanField(default=False)
    refund_requested= models.BooleanField(default=False)
    refund_granted= models.BooleanField(default=False)
    

    def __str__(self):
        return self.user.email
    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.getFinalPrice() 
        if self.coupon:
            total -= self.coupon.amount
        return total

class BillingModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment = models.CharField(max_length=100)
    country = CountryField(multiple=True)
    billingzip = models.CharField(max_length=100)
    addressType= models.CharField(max_length=1,  choices=ADDRESS_CHOICES )
    default= models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user.username

class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username 
class Coupon(models.Model):
    code = models.CharField(max_length=20)
    amount = models.FloatField()
    def __str__(self):
        return self.code

class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return self.order.user.email