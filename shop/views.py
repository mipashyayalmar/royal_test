from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from .forms import OrderUpdateForm  
from .models import Product, Contact, Orders, OrderUpdate
from django.contrib.auth.models import User
from django.contrib import messages
from math import ceil
from django.contrib.auth import authenticate, login, logout
import json
from django.views.decorators.csrf import csrf_exempt
from PayTm import Checksum
MERCHANT_KEY = 'kbzk1DSbJiV_O3p5';   
from django.utils.dateparse import parse_date
from django.db.models import Sum


def index(request):
    allProds = []
    categories = Product.objects.values('category', 'subcategory').distinct()
    cats = {item['category'] for item in categories}
    for cat in cats:
        subcats = {item['subcategory'] for item in categories if item['category'] == cat}
        cat_prods = []
        for subcat in subcats:
            prod = Product.objects.filter(category=cat, subcategory=subcat)
            cat_prods.append([subcat, prod])
        allProds.append([cat, cat_prods])
    context = {'allProds': allProds}
    return render(request, 'shop/index1.html', context)


def table_menu(request, category_id=None):
    allProds = []
    
    # Fetch distinct categories and subcategories
    categories = Product.objects.values('category', 'subcategory').distinct()
    
    # Create a set of distinct categories
    cats = {item['category'] for item in categories}
    
    # Iterate over each category
    for cat in cats:
        # Find distinct subcategories for the current category
        subcats = {item['subcategory'] for item in categories if item['category'] == cat}
        cat_prods = []
        
        # Iterate over each subcategory
        for subcat in subcats:
            # Retrieve products that match the category and subcategory
            prod = Product.objects.filter(category=cat, subcategory=subcat)
            cat_prods.append([subcat, prod])
        
        # Append the category and its corresponding products to allProds
        allProds.append([cat, cat_prods])
    
    # Include category_id in the context to use in the template
    context = {
        'allProds': allProds,
        'category_id': category_id,  # Pass the category_id to the context
    }
    
    return render(request, 'shop/table_menu.html', context)


from django.shortcuts import render, redirect
from .models import Advertise
from .forms import AdvertiseForm

def advertise(request):
    if request.method == 'POST':
        form = AdvertiseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('about')  # Redirect to the about page or another relevant page
    else:
        form = AdvertiseForm()
    return render(request, 'shop/advertise.html', {'form': form})

def about(request):
    advertisements = Advertise.objects.all()  # Get all advertisements
    return render(request, 'shop/about.html', {'advertisements': advertisements})

def contact(request):
    thank = False
    if request.method == "POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        thank = True
        return render(request, 'shop/contact.html', {'thank': thank})
    return render(request, 'shop/contact.html', {'thank': thank})


def tracker(request):
    if request.method == "POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        name = request.POST.get('name', '')
        password = request.POST.get('password')
        user = authenticate(username=name, password=password)
        if user is not None:
            try:
                order = Orders.objects.filter(order_id=orderId, email=email)
                if len(order) > 0:
                    update = OrderUpdate.objects.filter(order_id=orderId)
                    updates = []
                    for item in update:
                        updates.append({'text': item.update_desc, 'time': item.timestamp})
                        response = json.dumps({"status": "success", "updates": updates, "itemsJson": order[0].items_json}, default=str)
                    return HttpResponse(response)
                else:
                    return HttpResponse('{"status":"noitem"}')
            except Exception as e:
                return HttpResponse('{"status":"error"}')
        else:
            return HttpResponse('{"status":"Invalid"}')
    return render(request, 'shop/tracker.html')




def orderView(request):
    if request.user.is_authenticated:
        current_user = request.user
        orderHistory = Orders.objects.filter(userId=current_user.id)
        total_amount = 0
        
        if request.method == 'POST':
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')

            if start_date and end_date:
                start_date = parse_date(start_date)
                end_date = parse_date(end_date)
                orderHistory = orderHistory.filter(timestamp__date__range=(start_date, end_date))
                # Calculate the total amount for filtered orders
                total_amount = orderHistory.aggregate(total=Sum('amount'))['total'] or 0

        if len(orderHistory) == 0:
            messages.info(request, "You don't have any orders")
            return render(request, 'shop/orderView.html')

        return render(request, 'shop/orderView.html', {
            'orderHistory': orderHistory,
            'total_amount': total_amount,
        })
    
    return render(request, 'shop/orderView.html')

    
def searchMatch(query, item):
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower() or query in item.desc or query in item.product_name or query in item.category or query in item.desc.upper() or query in item.product_name.upper() or query in item.category.upper():
        return True
    else:
        return False
def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'subcategory', 'id')
    cats = {item['category'] for item in catprods}
    cart = request.session.get('cart', {})

    for cat in cats:
        subcats = {item['subcategory'] for item in catprods if item['category'] == cat}
        subcat_prods = []
        for subcat in subcats:
            prodtemp = Product.objects.filter(category=cat, subcategory=subcat)
            prod = [item for item in prodtemp if searchMatch(query, item) and str(item.id) not in cart]
            if len(prod) != 0:
                subcat_prods.append((subcat, prod))
        
        if len(subcat_prods) != 0:
            allProds.append((cat, subcat_prods))
        else:
            # If no subcategories, display products directly under the category
            prodtemp = Product.objects.filter(category=cat)
            prod = [item for item in prodtemp if searchMatch(query, item) and str(item.id) not in cart]
            if len(prod) != 0:
                allProds.append((cat, [("", prod)]))
    
    context = {'allProds': allProds, 'cart': cart, "msg": ""}
    if len(allProds) == 0 or len(query) < 3:
        context = {'msg': "No item available. Please make sure to enter relevant search query"}
    
    return render(request, 'shop/search.html', context)



# def checkout(request, category_id):
#     if request.method == "POST":
#         if 'order_lookup' in request.POST:
#             # Handle order lookup by order_id
#             order_id = request.POST.get('order_id', '')

#             try:
#                 order = Orders.objects.get(order_id=order_id)
#                 order_updates = OrderUpdate.objects.filter(order_id=order_id)
#                 items_json = json.loads(order.items_json)  # Assuming items_json is a JSON string
#                 return render(request, 'shop/checkout.html', {
#                     'order': order,
#                     'order_updates': order_updates,
#                     'order_found': True,
#                     'items': items_json,
#                     'category_id': category_id  # Pass category_id to template
#                 })
#             except Orders.DoesNotExist:
#                 return render(request, 'shop/checkout.html', {'order_not_found': True, 'category_id': category_id})

#         else:
#             # Handle the standard checkout process
#             user_id = request.POST.get('user_id', '')
#             if not user_id:
#                 messages.error(request, 'User ID is required.')
#                 return render(request, 'shop/checkout.html', {'order_not_found': True, 'category_id': category_id})

#             try:
#                 user_id = int(user_id)
#             except ValueError:
#                 messages.error(request, 'Invalid User ID.')
#                 return render(request, 'shop/checkout.html', {'order_not_found': True, 'category_id': category_id})

#             # Gather user input
#             name = request.POST.get('name', '')
#             email = request.POST.get('email', '')
#             address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
#             city = request.POST.get('city', '')
#             state = request.POST.get('state', '')
#             zip_code = request.POST.get('zip_code', '')
#             phone = request.POST.get('phone', '')
#             items_json = request.POST.get('itemsJson', '')
#             amount = request.POST.get('amount', '')
#             order_action = request.POST.get('order_action', 'new')

#             # Validate and convert amount
#             try:
#                 amount = float(amount) if amount else 0.0
#             except ValueError:
#                 messages.error(request, 'Invalid amount.')
#                 return render(request, 'shop/checkout.html', {'order_not_found': True, 'category_id': category_id})

#             # Store customer data in session
#             request.session['customer_data'] = {
#                 'user_id': user_id,
#                 'name': name,
#                 'email': email,
#                 'address': address,
#                 'city': city,
#                 'state': state,
#                 'zip_code': zip_code,
#                 'phone': phone
#             }

#             if order_action == 'update':
#                 order_id = request.POST.get('order_id', '')
#                 try:
#                     order = Orders.objects.get(order_id=order_id, userId=user_id)
#                     order.items_json = items_json
#                     order.name = name
#                     order.email = email
#                     order.address = address
#                     order.city = city
#                     order.state = state
#                     order.zip_code = zip_code
#                     order.phone = phone
#                     order.amount = amount
#                     order.save()

#                     update = OrderUpdate(order_id=order.order_id, update_desc="The Order has been Updated")
#                     update.save()

#                     messages.success(request, f"Order {order.order_id} successfully updated.")
#                     id = order.order_id
#                 except Orders.DoesNotExist:
#                     messages.error(request, 'Order not found or invalid.')
#                     return render(request, 'shop/checkout.html', {'order_not_found': True, 'category_id': category_id})

#             else:
#                 # Create a new order
#                 order = Orders(
#                     items_json=items_json,
#                     userId=user_id,
#                     name=name,
#                     email=email,
#                     address=address,
#                     city=city,
#                     state=state,
#                     zip_code=zip_code,
#                     phone=phone,
#                     amount=amount
#                 )
#                 order.save()

#                 update = OrderUpdate(order_id=order.order_id, update_desc="The Order has been Placed")
#                 update.save()

#                 messages.success(request, f"Order {order.order_id} successfully created.")
#                 id = order.order_id

#             # Payment processing
#             if 'onlinePay' in request.POST:
#                 # Handle online payment
#                 darshan_dict = {
#                     'MID': 'WorldP64425807474247',  # Your-Merchant-Id-Here
#                     'ORDER_ID': str(order.order_id),
#                     'TXN_AMOUNT': str(amount),
#                     'CUST_ID': email,
#                     'INDUSTRY_TYPE_ID': 'Retail',
#                     'WEBSITE': 'WEBSTAGING',
#                     'CHANNEL_ID': 'WEB',
#                     'CALLBACK_URL': 'http://127.0.0.1:8000/shop/handlerequest/',
#                 }
#                 darshan_dict['CHECKSUMHASH'] = Checksum.generate_checksum(darshan_dict, MERCHANT_KEY)
#                 return render(request, 'shop/paytm.html', {'darshan_dict': darshan_dict})

#             elif 'cashOnDelivery' in request.POST:
#                 return render(request, 'shop/checkout.html', {'thank': True, 'id': id, 'category_id': category_id})

#     # Render the checkout page with category_id
#     return render(request, 'shop/checkout.html', {
#     'category_id': category_id,
#     # other context variables...
# })

def checkout(request, category_id):
    if request.method == "POST":
        if 'order_lookup' in request.POST:
            # Handle order lookup by order_id
            order_id = request.POST.get('order_id', '')

            try:
                order = Orders.objects.get(order_id=order_id)
                order_updates = OrderUpdate.objects.filter(order_id=order_id)
                items_json = json.loads(order.items_json)
                return render(request, 'shop/checkout.html', {
                    'order': order,
                    'order_updates': order_updates,
                    'order_found': True,
                    'items': items_json,
                    'category_id': category_id  # Include category_id in context
                })
            except Orders.DoesNotExist:
                return render(request, 'shop/checkout.html', {'order_not_found': True, 'category_id': category_id})

        else:
            # Handle the standard checkout process
            user_id = request.POST.get('user_id', '')
            if not user_id:
                messages.error(request, 'User ID is required.')
                return render(request, 'shop/checkout.html', {'order_not_found': True, 'category_id': category_id})

            try:
                user_id = int(user_id)
            except ValueError:
                messages.error(request, 'Invalid User ID.')
                return render(request, 'shop/checkout.html', {'order_not_found': True, 'category_id': category_id})

            name = request.POST.get('name', '')
            email = request.POST.get('email', '')
            address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
            city = request.POST.get('city', '')
            state = request.POST.get('state', '')
            zip_code = request.POST.get('zip_code', '')
            phone = request.POST.get('phone', '')
            items_json = request.POST.get('itemsJson', '')
            amount = request.POST.get('amount', '')
            order_action = request.POST.get('order_action', 'new')

            # Validate and convert amount
            try:
                amount = float(amount) if amount else 0.0
            except ValueError:
                messages.error(request, 'Invalid amount.')
                return render(request, 'shop/checkout.html', {'order_not_found': True, 'category_id': category_id})

            # Store customer data in session
            request.session['customer_data'] = {
                'user_id': user_id,
                'name': name,
                'email': email,
                'address': address,
                'city': city,
                'state': state,
                'zip_code': zip_code,
                'phone': phone
            }

            if order_action == 'update':
                order_id = request.POST.get('order_id', '')
                try:
                    order = Orders.objects.get(order_id=order_id, userId=user_id)
                    order.items_json = items_json
                    order.name = name
                    order.email = email
                    order.address = address
                    order.city = city
                    order.state = state
                    order.zip_code = zip_code
                    order.phone = phone
                    order.amount = amount
                    order.save()

                    update = OrderUpdate(order_id=order.order_id, update_desc="The Order has been Updated")
                    update.save()

                    messages.success(request, f"Order {order.order_id} successfully updated.")
                    id = order.order_id
                except Orders.DoesNotExist:
                    messages.error(request, 'Order not found or invalid.')
                    return render(request, 'shop/checkout.html', {'order_not_found': True, 'category_id': category_id})

            else:
                # Create a new order
                order = Orders(
                    items_json=items_json,
                    userId=user_id,
                    name=name,
                    email=email,
                    address=address,
                    city=city,
                    state=state,
                    zip_code=zip_code,
                    phone=phone,
                    amount=amount
                )
                order.save()

                update = OrderUpdate(order_id=order.order_id, update_desc="The Order has been Placed")
                update.save()

                messages.success(request, f"Order {order.order_id} successfully created.")
                id = order.order_id

            if 'onlinePay' in request.POST:
                # Handle online payment
                darshan_dict = {
                    'MID': 'WorldP64425807474247',
                    'ORDER_ID': str(order.order_id),
                    'TXN_AMOUNT': str(amount),
                    'CUST_ID': email,
                    'INDUSTRY_TYPE_ID': 'Retail',
                    'WEBSITE': 'WEBSTAGING',
                    'CHANNEL_ID': 'WEB',
                    'CALLBACK_URL': 'http://127.0.0.1:8000/shop/handlerequest/',
                }
                darshan_dict['CHECKSUMHASH'] = Checksum.generate_checksum(darshan_dict, MERCHANT_KEY)
                return render(request, 'shop/paytm.html', {'darshan_dict': darshan_dict})

            elif 'cashOnDelivery' in request.POST:
                return render(request, 'shop/checkout.html', {'order_not_found': True, 'category_id': category_id})

    return render(request, 'shop/checkout.html', {'order_not_found': True, 'category_id': category_id})

def productView(request, myid):
    product = get_object_or_404(Product, id=myid)
    cart = request.session.get('cart', {})

    if request.method == 'POST':
        qty = int(request.POST.get('qty', 1))
        if myid in cart:
            cart[myid][0] += qty
        else:
            cart[myid] = [qty, product.product_name, product.price]
        request.session['cart'] = cart
        messages.success(request, 'Product added to cart')
        return redirect('shop:productView', myid=myid)

    return render(request, 'shop/prodView.html', {'product': product})


def handeLogin(request):
    if request.method == "POST":
        # Get the post parameters
        loginusername = request.POST['loginusername']
        loginpassword = request.POST['loginpassword']

        user = authenticate(username=loginusername, password=loginpassword)
        if user is not None:
            login(request, user)
            messages.success(request, "Successfully Logged In")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.warning(request, "Invalid credentials! Please try again")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return HttpResponse("404- Not found")


def handleSignUp(request):
    if request.method == "POST":
        # Get the post parameters
        username = request.POST['username']
        f_name = request.POST['f_name']
        l_name = request.POST['l_name']
        email = request.POST['email1']
        phone = request.POST['phone']
        password = request.POST['password']
        password1 = request.POST['password1']

        # check for errorneous input
        if (password1 != password):
            messages.warning(request, " Passwords do not match")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        try:
            user = User.objects.get(username=username)
            messages.warning(request, " Username Already taken. Try with different Username.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except User.DoesNotExist:
            # Create the user
            myuser = User.objects.create_user(username=username, email=email, password=password)
            myuser.first_name = f_name
            myuser.last_name = l_name
            myuser.phone = phone
            myuser.save()
            messages.success(request, " Your Account has been successfully created")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponse("404 - Not found")


def handleLogout(request):
    logout(request)
    messages.success(request, "Successfully logged out")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request, 'shop/paymentstatus.html', {'response': response_dict})




def update_order(request):
    if request.method == "POST":
        order_id = request.POST.get('order_id', '')

        try:
            order = Orders.objects.get(order_id=order_id)
            order_updates = OrderUpdate.objects.filter(order_id=order_id)
            items_json = json.loads(order.items_json)  # Assuming items_json is a JSON string
            return render(request, 'shop/updateorder.html', {
                'order': order, 
                'order_updates': order_updates, 
                'order_found': True, 
                'items': items_json
            })
        except Orders.DoesNotExist:
            return render(request, 'shop/updateorder.html', {'order_not_found': True})
    
    return render(request, 'shop/update_order.html', {
        'form': form,
        'form_data_json': json.dumps(form_data_json),
        'amount': order.amount,
    })
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Orders
from .forms import OrderUpdateForm
import json
def update_order(request, order_id):
    # Retrieve the order instance
    order = get_object_or_404(Orders, order_id=order_id)
    
    if request.method == 'POST':
        form = OrderUpdateForm(request.POST, instance=order)
        if form.is_valid():
            updated_order = form.save(commit=False)
            updated_order.items_json = request.POST.get('items_json')  # Update items_json
            updated_order.amount = request.POST.get('amount')          # Update amount
            updated_order.save()
            
            name = updated_order.name  # Assuming 'name' is a field in the Orders model
            amount = updated_order.amount  # Get the updated amount
            
            messages.success(request, f"Order {order_id} successfully updated by {name} with amount Rs. {amount}.")
            return redirect('shop:orderView')  # Ensure this name matches the URL pattern name
    else:
        # Prepare the form with existing order data for GET requests
        form = OrderUpdateForm(instance=order)
    
    # Prepare form data and cart data in JSON format
    form_data_json = {field: form.initial.get(field, '') for field in form.fields}
    cart_data = json.loads(order.items_json) if order.items_json else {}
    
    return render(request, 'shop/update_order.html', {
        'form': form,
        'form_data_json': json.dumps(form_data_json),  # Convert form data to JSON string
        'cart_data_json': json.dumps(cart_data),        # Convert cart data to JSON string
        'order': order  # Pass the order object to the template
    })
