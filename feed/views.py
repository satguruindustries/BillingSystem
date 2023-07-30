from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from .forms import NewProductForm,InvoiceForm,InvoiceItemForm
from django.views.generic import ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Product,invoice,InvoiceItem
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from users.models import Profile
from django.utils.decorators import method_decorator
from django import forms

import json
global sub
sub = "Physics"
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
        context['sub'] = sub
        context['form'] = InvoiceForm()
        context['itemform'] = InvoiceItemForm()
        last=1
        last_invoice = invoice.objects.order_by('-invoice_num').first()
        if last_invoice:
            last = last_invoice.invoice_num + 1
        else:
            last = 1 
        context['invoice_num'] = last
        return context

def updatesub(request,name):
    global sub
    sub = name
    return redirect('home')


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


def post_detail(request, pk):
    my_invoice = get_object_or_404(invoice, pk=pk)
    invoice_items = InvoiceItem.objects.filter(invoice=my_invoice)
    user = request.user
    return render(request, 'feed/invoice_detail.html', {'invoice':my_invoice, 'invoice_items':invoice_items})

def create_post(request):
    user = request.user
    if request.method == "POST":
        form = NewProductForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            data.user_name = user
            data.save()
            messages.success(request, f'Posted Successfully')
            return redirect('home')
    else:
        form = NewProductForm()
    return render(request, 'feed/create_post.html', {'form':form})

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = invoice
    form_class = InvoiceForm
    template_name = 'feed/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allprod'] = Product.objects.all()
        if self.request.method == 'POST':
            context['form'] = InvoiceForm(self.request.POST, instance=self.object)
            context['item_forms'] = [InvoiceItemForm(self.request.POST, prefix=f'item_{item.id}', instance=item) for item in InvoiceItem.objects.filter(invoice=self.object)]
        else:
            context['form'] = InvoiceForm(instance=self.object)

            # Create the "products" queryset containing all items from Product.objects.all()
            products_queryset = Product.objects.all()
            item_forms = []
            # Set up the InvoiceItemForm instances with initial product data
            for item in InvoiceItem.objects.filter(invoice=self.object):
                # Create a new form instance for each item
                item_form = InvoiceItemForm(prefix=f'item_{item.id}', instance=item)
                # Add a new 'products' field to each form and set its queryset
                item_form.fields['products'] = forms.ModelChoiceField(queryset=products_queryset, initial=item.product.id if item.product else None)
                item_forms.append(item_form)

            context['item_forms'] = item_forms

        return context

    def form_valid(self, form):
        form.instance.user_name = self.request.user

        # Save the updated invoice
        response = super().form_valid(form)

        # Save the invoice items
        item_forms = self.get_context_data()['item_forms']
        for item_form in item_forms:
            if item_form.is_valid():
                item_form.instance.invoice = self.object
                item_form.save()

        return response

    def test_func(self):
        invoice = self.get_object()
        return True

def post_delete(request, pk):
    post = Product.objects.get(pk=pk)
    if request.user== post.user_name:
        Product.objects.get(pk=pk).delete()
    return redirect('home')


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
            totals = request.POST.getlist('total')
            all_prod = Product.objects.all()
            # Loop through the product details and create InvoiceItem objects
            for product_name, quantity, total in zip(product_names, quantities, totals):
                product = all_prod[int(product_name)-1]
                InvoiceItem.objects.create(invoice=invoice_obj, product=product, quantity=quantity, total=total)

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
