from django.shortcuts import render, get_object_or_404, redirect
from .models import Item,OrderItem,Order,BillingModel,Payment,Coupon,Refund
from django.views.generic import ListView,DetailView, View
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm,CouponForm,RefundForm
from django.conf import settings
import random
import string
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

def CreateRefCode():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


# `source` is obtained with Stripe.js; see https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token
def isValid(values):
    valid = True
    for value in values:
        if value == '':
            valid =False
    return valid

class Home(ListView):
    template_name = "home.html"
    model = Item
    paginate_by = 12
 

class Checkout(View):
    def get(self, *args, **kwargs):
        try: 
            order = Order.objects.get(user=self.request.user, ordered=False)            
            form   = CheckoutForm()
            context = {
                "form":form,
                "order":order,
                "couponform":CouponForm(),
                'DisplayCouponForm':True

            }
            shippingAddressQs = BillingModel.objects.filter(
                user=self.request.user,
                addressType ='S',
                default=True
            )
            if shippingAddressQs.exists():
                context.update({'use_default_shipping':shippingAddressQs[0]})
            BillingAddressQs = BillingModel.objects.filter(
                user=self.request.user,
                addressType ='B',
                default=True
            )
            if shippingAddressQs.exists():
                context.update({'use_default_billing':shippingAddressQs[0]})
            return render(self.request, 'checkout-page.html',context)
        except ObjectDoesNotExist:
            messages.info(self.request, "you dont have an active order", extra_tags="danger")
            return redirect("app:checkout")

        
    def post(self, *args, **kwargs):
        form   = CheckoutForm(self.request.POST or None)
        try:
            order= Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                use_default_shipping = form.cleaned_data.get('use_default_shipping')
                

                if use_default_shipping:
                    print('hello world')
                    AddressQs = BillingModel.objects.filter(
                        user=self.request.user,
                        addressType ='S',
                        default=True
                    )
                    if AddressQs.exists():
                        shippingaddress = AddressQs[0]
                        order.shipping_address = shippingaddress
                        order.save()
                    else:
                        messages.info(self.request, 'no default shipping address available')
                        return redirect('app:checkout')
                else:
                    print('user is entering a new shipping address')

                    shippingAddress  = form.cleaned_data.get('shippingAddress')
                    shippingAddress2   = form.cleaned_data.get('shippingAddress')
                    shippingCountry= form.cleaned_data.get('shippingCountry')
                    shippingZip= form.cleaned_data.get('shippingZip')
                    
                    if isValid([shippingAddress,shippingCountry,shippingZip]):
                        shipping_address = BillingModel(
                            user=self.request.user,
                            street_address = shippingAddress,
                            apartment = shippingAddress2,
                            country = shippingCountry,
                            billingzip = shippingZip,
                            addressType = 'S'
                        )
                        shipping_address.save()
                        order.shipping_address =shipping_address
                        order.save()
                        set_default_shipping = form.cleaned_data.get('set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()
                    else:
                        messages.info(self.request,'fill in the required fields')
                        return redirect('app:checkout')
                    

                use_default_billing = form.cleaned_data.get('use_default_billing')
                same_billing_address = form.cleaned_data.get('same_billing_address')
                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.addressType = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()
                elif use_default_billing:
                    print('hello Africa')
                    BillingQs = BillingModel.objects.filter(
                        user=self.request.user,
                        addressType ='S',
                        default=True
                    )
                    if BillingQs.exists():
                        billingaddress = AddressQs[0]
                        order.billing_address = billingaddress
                        order.save()
                    else:
                        messages.info(self.request, 'no default billing address available')
                        return redirect('app:checkout')
                else:
                    print('user is entering a new shipping address')

                    billingAddress  = form.cleaned_data.get('billingAddress')
                    billingAddress2   = form.cleaned_data.get('billingAddress2')
                    billingCountry= form.cleaned_data.get('billingCountry')
                    billingZip= form.cleaned_data.get('billingZip')
                    if isValid([billingAddress,billingCountry,billingZip]):
                        billing_address = BillingModel(
                            user=self.request.user,
                            street_address = billingAddress,
                            apartment = billingAddress2,
                            country = billingCountry,
                            billingzip = billingZip,
                            addressType = 'B'
                        )
                        billing_address.save()

                        order.billing_address =billing_address
                        order.save()
                        set_default_billing = form.cleaned_data.get('set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()
                    else:
                        messages.info(self.request,'fill in the required fields')
                        return redirect('app:checkout')
                    
                paymentOption= form.cleaned_data.get('paymentOption')
                if paymentOption == 'S':
                    return redirect('app:PaymentView', payment_option ='Stripe')
                elif paymentOption == 'P':
                    return redirect('app:PaymentView', payment_option ='Paystack')
                
                else:
                    messages.warning(self.request, "choose a payment option")
                    return redirect('app:checkout')
            # messages.warning(self.request, "invalid form")
            # return redirect('app:checkout')
        except ObjectDoesNotExist:
            messages.error(request, "you dont have an order", extra_tags='danger')
            return redirect('app:Ordersummary')
        
        
class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                "order":order,
                'DisplayCouponForm':False
            }
            return render(self.request, 'payment.html',context)
        else:
            messages.info(self.request, "you have not added a billing address", extra_tags="danger")
            return redirect('app:checkout')
    def post(self, *args, **kwargs):
        try: 
            order = Order.objects.get(user=self.request.user, ordered=False)
            token = self.request.POST.get('stripeToken')
            charge = stripe.Charge.create(
            amount=int(order.get_total()),
            currency="usd",
            source=token,
            )
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            order_item = order.items.all()
            order_item.update(ordered=True)

            for item in order_item:
                item.save()

            order.ordered = True
            order.payment = payment
            order.ref_code =CreateRefCode()
            
            order.save()

            messages.success(self.request, 'your order was successful', extra_tags="success")
            return redirect("app:home")
        except stripe.error.CardError as e:
        # Since it's a decline, stripe.error.CardError will be caught
            messages.error(self.request, "card was declined",extra_tags="danger")
            return redirect("app:home")
        
        except stripe.error.RateLimitError as e:
        # Too many requests made to the API too quickly
            messages.error(self.request, "rate limit error",extra_tags="danger")
            return redirect("app:home")
        except stripe.error.InvalidRequestError as e:
            print(e)
            messages.error(self.request, "invalid parameters were supplied",extra_tags="danger")
            return redirect("app:home")
        # Invalid parameters were supplied to Stripe's API
        
        except stripe.error.AuthenticationError as e:
        # Authentication with Stripe's API failed
        # (maybe you changed API keys recently)
            messages.error(self.request, "failed Authentication.",extra_tags="danger")
            return redirect("app:home")
       
        except stripe.error.APIConnectionError as e:
        # Network communication with Stripe failed
            messages.error(self.request, "poor Network communication.",extra_tags="danger")
            return redirect("app:home")
        except stripe.error.StripeError as e:
            messages.error(self.request, "something went wrong, you were not charged, please try again.",extra_tags="danger")
            return redirect("app:home")
        # Display a very generic error to the user, and maybe send
        # yourself an email
        
        except Exception as e:
            messages.error(self.request, "an error occured, we have been notified.",extra_tags="danger")
            return redirect("app:home")
        # Something else happened, completely unrelated to Stripe
       


class Ordersummary(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
                   
            context = {
                'object': order,
                # "order":order
            }
            return render(self.request, "order_summary.html", context)
        except ObjectDoesNotExist:
            messages.error(self.request, "you don't have an active order", extra_tags='danger')
            return redirect('/')

        

class ItemDetailView(DetailView):
    model = Item
    template_name = 'product-page.html'


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(item=item, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request,"this item quantity was updated",extra_tags="primary")
            return redirect("app:Ordersummary")
        else:
            messages.info(request, "this item was added to your cart", extra_tags="success")
            order.items.add(order_item)
            return redirect("app:Ordersummary")
    else: 
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        return redirect("app:product",slug=slug)

@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "this item was removed from your cart.", extra_tags="warning")
            return redirect("app:Ordersummary")
        else:
            messages.info(request, "this item was not in your cart", extra_tags="danger")
            return redirect("app:product",slug=slug)
    else: 
        messages.info(request, "you do not have an active order", extra_tags="danger")
        return redirect("app:product",slug=slug)
    return redirect("app:product",slug=slug)
@login_required
def remove_single_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                messages.info(request, "this item quantity was reduced", extra_tags="warning")
                return redirect("app:Ordersummary")
            else:
                order.items.remove(order_item)
                order_item.delete()
                messages.info(request, "this item quantity was removed from your cart", extra_tags="warning")
                return redirect("app:Ordersummary")
        else:
            messages.info(request, "this item was not in your cart", extra_tags="danger")
            return redirect("app:product",slug=slug)
    else: 
        messages.info(request, "you do not have an active order", extra_tags="danger")
        return redirect("app:product",slug=slug)
    return redirect("app:product",slug=slug)


def get_coupon(request, code):
    
    try: 
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "this coupon does not exist", extra_tags="danger")
        return redirect("app:checkout")
        
class AddCoupon(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try: 
                code = form.cleaned_data.get('code')
                order = Order.objects.get(user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.info(self.request, "successfully added coupon", extra_tags="success")
                return redirect("app:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "this coupon does not exist", extra_tags="danger")
                return redirect("app:checkout")

class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            "form": form
        }
        return render(self.request, "request-refund.html", context)
    def post(self, *args, **kwargs):
        form =RefundForm(self.request.POST or None)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message  = form.cleaned_data.get('message')
            email  = form.cleaned_data.get('email')
            try:
                order =Order.objects.get(ref_code=ref_code, user__email=email)
                order.refund_requested = True
                order.save()
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()
                messages.info(self.request, "your request will be reviewed", extra_tags="danger")
                return redirect('app:RequestRefundView')
            except ObjectDoesNotExist:
                messages.info(self.request, "this order does not exist", extra_tags="danger")
                return redirect('app:RequestRefundView')