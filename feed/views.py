from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, UpdateView, DeleteView
from django.views.decorators.http import require_POST
from .models import Product,invoice,InvoiceItem,Stock,SellStock
from .forms import NewProductForm,InvoiceForm,InvoiceItemForm,StockForm,SellStockForm
from users.models import Profile
from django.db.models import Sum
from django.utils import timezone
from django.utils.decorators import method_decorator
from django import forms

import json

@method_decorator(login_required, name='dispatch')
class PostListView(ListView):
    model = Product
    template_name = 'feed/home.html'
    context_object_name = 'posts'
    paginate_by = 10
    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            p = Profile.objects.get(user=self.request.user)
            friends = p.friends.all()
            context['friends'] = friends
        context['form'] = InvoiceForm()
        context['itemform'] = InvoiceItemForm()

        current_year = timezone.now().year
        next_year = current_year + 1
        financial_year = f"{current_year % 100:02d}-{next_year % 100:02d}"
        # Get the count of invoices for the current financial year
        invoices_count = invoice.objects.filter(invoice_num__contains=financial_year).count()
        invoice_number = 1
        
        if invoices_count:
            invoice_number = invoices_count + 1
            
        invoice_num = f"INV/{financial_year}/{invoice_number}"
        context['invoice_num'] = invoice_num
        
        return context

@method_decorator(login_required, name='dispatch')
class UserPostListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'feed/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(UserPostListView, self).get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        liked = [i for i in Product.objects.filter(user_name=user) if Like.objects.filter(user = self.request.user, post=i)]
        context['liked_post'] = liked
        return context

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Product.objects.filter(user_name=user).order_by('-date_posted')

@login_required
def post_detail(request, pk):
    my_invoice = get_object_or_404(invoice, pk=pk)
    invoice_items = InvoiceItem.objects.filter(invoice=my_invoice)
    user = request.user
    return render(request, 'feed/invoice_detail.html', {'invoice':my_invoice, 'invoice_items':invoice_items})

@login_required
def create_post(request):
    if request.user.is_authenticated:
        user = request.user
        if request.method == "POST":
            form = NewProductForm(request.POST, request.FILES)
            if form.is_valid():
                data = form.save(commit=False)
                data.user_name = user
                data.save()
                messages.success(request, f'Posted Successfully')
                return redirect('products')
        else:
            form = NewProductForm()
    else:
        return redirect('products')
    return render(request, 'feed/create_post.html', {'form':form})

@login_required
def product_update(request, pk):
    user = request.user
    
    if pk:
        post = get_object_or_404(Product, id=pk)
    else:
        post = None
    
    if request.method == "POST":
        form = NewProductForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            data = form.save(commit=False)
            data.user_name = user
            data.save()
            messages.success(request, 'Post Updated Successfully' if post else 'Posted Successfully')
            return redirect('products')
    else:
        form = NewProductForm(instance=post)
    
    return render(request, 'feed/create_post.html', {'form': form})

@method_decorator(login_required, name='dispatch')
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = invoice
    form_class = InvoiceForm
    template_name = 'feed/update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allprod'] = Product.objects.all()
        if self.request.method == 'POST':
            context['form'] = InvoiceForm(self.request.POST, instance=self.object)
            context['item_forms'] = [InvoiceItemForm(self.request.POST, instance=item) for item in InvoiceItem.objects.filter(invoice=self.object)]
        else:
            context['form'] = InvoiceForm(instance=self.object)
            context['posts'] = Product.objects.all()

            # Create the "products" queryset containing all items from Product.objects.all()
            products_queryset = Product.objects.all()
            item_forms = []
            # Set up the InvoiceItemForm instances with initial product data
            for item in InvoiceItem.objects.filter(invoice=self.object):
                # Create a new form instance for each item
                item_form = InvoiceItemForm(instance=item)
                # Add a new 'products' field to each form and set its queryset
                item_form.fields['products'] = forms.ModelChoiceField(queryset=products_queryset, initial=item.product.id if item.product else None)
                item_forms.append(item_form)

            context['item_forms'] = item_forms

        return context

    def form_valid(self, form):
        form.instance.user_name = self.request.user

        # Save the updated invoice
        response = super().form_valid(form)

        # Delete all existing invoice items for the current invoice
        InvoiceItem.objects.filter(invoice=self.object).delete()

        # Get the selected products from the form
        product_names = self.request.POST.getlist('products')
        quantities = self.request.POST.getlist('quantity')
        rates = self.request.POST.getlist('rate')
        totals = self.request.POST.getlist('total')

        # Ensure that the number of selected products matches the number of invoice items
        if len(product_names) > 0:
            all_prod = Product.objects.all()
            invoice_obj = self.object
            # Loop through the product details and create InvoiceItem objects
            for product_name, quantity, total, rate in zip(product_names, quantities, totals, rates):
                product = Product.objects.get(id=product_name)
                InvoiceItem.objects.create(invoice=invoice_obj, product=product, rate=rate, quantity=quantity, total=total)

            # Calculate the grand total and save it in the invoice
            grand_total = sum(float(total) for total in totals) + float(form.instance.freight_charges)
            invoice_obj.grand_total = grand_total
            invoice_obj.save()

        return response

    def test_func(self):
        invoice = self.get_object()
        return True

@login_required
def product_delete(request, pk):
    post = Product.objects.get(pk=pk)
    if request.user.is_authenticated:
        post.delete()
    return redirect('products')

@login_required
def search(request):
    query = request.GET.get('p')
    if(not query):
        return redirect('invoices')
    invoices_list = invoice.objects.filter(invoice_num__icontains=query)
    customers_list = invoice.objects.filter(cust_name__icontains=query)
    context ={
        'invoices_list': invoices_list,
        'customers_list': customers_list
    }
    return render(request, "feed/invoices.html", context)

@method_decorator(login_required, name='dispatch')
class explore_posts(ListView):
    model = Product
    template_name = 'feed/explore.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 10
    def get_context_data(self, **kwargs):
        context = super(explore_posts, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            p = Profile.objects.get(user=self.request.user)
            friends = p.friends.all()
            context['friends'] = friends
            liked = [i for i in Product.objects.all() if Like.objects.filter(user = self.request.user, post=i).exists()]
            context['liked_post'] = liked
        return context
    
@method_decorator(login_required, name='dispatch')
class invoices(ListView):
    model = invoice
    template_name = 'feed/invoices.html'
    context_object_name = 'posts'
    paginate_by = 10
    ordering = ['-id']
    def get_context_data(self, **kwargs):
        context = super(invoices, self).get_context_data(**kwargs)
        query = self.request.GET.get('p')
        if(not query):
            return context
        invoices_list = invoice.objects.filter(invoice_num__icontains=query)
        customers_list = invoice.objects.filter(cust_name__icontains=query)
        context['invoices_list'] = invoices_list
        context['customers_list'] = customers_list
        return context

@method_decorator(login_required, name='dispatch')
class dashboard(ListView):
    model = Stock
    template_name = 'feed/dashboard.html'
    context_object_name = 'posts'
    ordering = ['-date']
    def get_context_data(self, **kwargs):
        context = super(dashboard, self).get_context_data(**kwargs)
        context['form'] = StockForm(prefix='stock')
        context['sellform'] = SellStockForm(prefix='sell_stock')
        context['sold'] = SellStock.objects.all()
        
        a_total_quantity = Stock.objects.filter(product_id=1).aggregate(total_quantity=Sum('quantity'))['total_quantity']
        a_transfered = Stock.objects.filter(product_id=1).aggregate(transfered=Sum('transfer'))['transfered']
        a_sold = SellStock.objects.filter(product_id=1).aggregate(sold=Sum('quantity'))['sold']
        b_total_quantity = Stock.objects.filter(product_id=8).aggregate(total_quantity=Sum('quantity'))['total_quantity']
        b_transfered = Stock.objects.filter(product_id=8).aggregate(transfered=Sum('transfer'))['transfered']
        b_sold = SellStock.objects.filter(product_id=8).aggregate(sold=Sum('quantity'))['sold']
        if(a_total_quantity==None):
            a_total_quantity=0
        
        if(a_transfered==None):
            a_transfered=0
        
        if(a_sold==None):
            a_sold=0
        
        if(b_total_quantity==None):
            b_total_quantity=0
        
        if(b_transfered==None):
            b_transfered=0
        
        if(b_sold==None):
            b_sold=0
        
        context['a_ground_stock'] = a_total_quantity-a_transfered
        context['a_main_stock'] = a_transfered - a_sold
        context['b_ground_stock'] = b_total_quantity-b_transfered
        context['b_main_stock'] = b_transfered - b_sold

        context['a_sold'] = a_sold
        context['b_sold'] = b_sold

        return context

@login_required
def newStockItem(request):
    if request.user.is_authenticated:
        user = request.user
        if request.method == "POST":
            form = StockForm(request.POST, prefix='stock')
            if form.is_valid():
                date = form.cleaned_data['date']
                quantity = form.cleaned_data['quantity']
                transfer = form.cleaned_data['transfer']
                product_names = request.POST.getlist('stock-products')
                all_prod = Product.objects.all()
                for product_name in product_names:
                    product = get_object_or_404(Product, pk=int(product_name))
                    stocks_list = Stock.objects.filter(date__icontains=date, product=product)
                    if stocks_list.exists():
                        stock = stocks_list[0]
                        stock.quantity += quantity
                        stock.transfer += transfer
                        stock.save()
                        return redirect('dashboard')
                    stock_obj = Stock.objects.create(date=date, product=product, quantity=quantity, transfer=transfer)
                    stock_obj.save()
                messages.success(request, f'Posted Successfully')
                return redirect('dashboard')
            
        else:
            form = StockForm()
    else:
        return redirect('dashboard')
    return redirect('dashboard')

@login_required
def newSellStockItem(request):
    if request.user.is_authenticated:
        user = request.user
        if request.method == "POST":
            form = SellStockForm(request.POST, prefix='sell_stock')
            if form.is_valid():
                date = form.cleaned_data['date']
                quantity = form.cleaned_data['quantity']
                product_names = request.POST.getlist('sell_stock-products')
                all_prod = Product.objects.all()
                for product_name in product_names:
                    product = get_object_or_404(Product, pk=int(product_name))
                    stocks_list = SellStock.objects.filter(date__icontains=date, product=product)
                    if stocks_list.exists():
                        stock = stocks_list[0]
                        stock.quantity += quantity
                        stock.save()
                        return redirect('dashboard')
                    stock_obj = SellStock.objects.create(date=date, product=product, quantity=quantity)
                    stock_obj.save()
                messages.success(request, f'Sell Posted Successfully')
                return redirect('dashboard')
            
        else:
            form = SellStockForm()
    else:
        return redirect('dashboard')
    return redirect('dashboard')

@login_required
def stock_item_delete(request, pk):
    item = Stock.objects.get(pk=pk)
    if request.user.is_authenticated:
        item.delete()
    return redirect('dashboard')

@login_required
def sell_stock_item_delete(request, pk):
    item = SellStock.objects.get(pk=pk)
    if request.user.is_authenticated:
        item.delete()
    return redirect('dashboard')

@method_decorator(login_required, name='dispatch')
class products(ListView):
    model = Product
    template_name = 'feed/products.html'
    context_object_name = 'posts'
    paginate_by = 10
    ordering = ['-id']
    def get_context_data(self, **kwargs):
        context = super(products, self).get_context_data(**kwargs)
        query = self.request.GET.get('p')
        if(not query):
            return context
        products_list = Product.objects.filter(name__icontains=query)
        hsn_list = Product.objects.filter(hsn__icontains=query)
        context['products_list'] = products_list
        context['hsn_list'] = hsn_list
        return context

@login_required
def like(request):
    post_id = request.GET.get("likeId", "")
    user = request.user
    post = Product.objects.get(pk=post_id)
    liked= False
    like = Like.objects.filter(user=user, post=post)
    if like:
        like.delete()
    else:
        liked = True
        Like.objects.create(user=user, post=post)
    resp = {
        'liked':liked
    }
    response = json.dumps(resp)
    return HttpResponse(response, content_type = "application/json")

@login_required
def save_invoice(request):
    user = request.user
    if request.method == "POST":
        form = InvoiceForm(request.POST, request.FILES)
        itemform = InvoiceItemForm(request.POST, request.FILES)
        if form.is_valid() and itemform.is_valid():
            # Process the form data and create the invoice object
            cust_name = form.cleaned_data['cust_name']
            cust_add = form.cleaned_data['cust_add']
            cust_place = form.cleaned_data['cust_place']
            cust_gstin = form.cleaned_data['cust_gstin']
            invoice_num = form.cleaned_data['invoice_num']
            date = form.cleaned_data['date']
            freight_charges = form.cleaned_data['freight_charges']

            invoice_obj = invoice.objects.create(
                cust_name=cust_name,
                cust_add=cust_add,
                cust_place=cust_place,
                cust_gstin=cust_gstin,
                invoice_num=invoice_num,
                date=date,
                freight_charges=freight_charges,
            )

            # Process invoice items
            product_names = request.POST.getlist('products')
            quantities = request.POST.getlist('quantity')
            rates = request.POST.getlist('rate')
            totals = request.POST.getlist('total')
            all_prod = Product.objects.all()
            # Loop through the product details and create InvoiceItem objects
            for product_name, quantity, total, rate in zip(product_names, quantities, totals, rates):
                product_id = int(product_name)
                product = Product.objects.get(id=product_id)
                InvoiceItem.objects.create(invoice=invoice_obj, product=product, quantity=quantity, rate=rate, total=total)

            # Calculate the grand total and save it in the invoice
            grand_total = sum(float(total) for total in totals) + float(freight_charges)
            invoice_obj.grand_total = grand_total
            invoice_obj.save()

            messages.success(request, 'Invoice posted successfully.')
            return redirect('post-detail', pk=invoice_obj.id)
        else:
            messages.error(request, 'Form is invalid. Please check the entries.')
    else:
        form = InvoiceForm()
    return redirect('home')
