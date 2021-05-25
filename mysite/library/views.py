from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin

from django.contrib.auth.forms import User
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages


from .models import Book, Author, BookInstance, Genre
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView)

from .forms import BookReviewForm,UserUpdateForm, ProfilisUpdateForm
from django.utils.translation import gettext as _

# Importuojame FormMixin, kurį naudosime BookDetailView klasėje
from django.views.generic.edit import FormMixin


#------function based views:
def index(request):
    # Suskaičiuokime keletą pagrindinių objektų
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Laisvos knygos (tos, kurios turi statusą 'g')
    num_instances_available = BookInstance.objects.filter(status__exact='g').count()

    # Kiek yra autorių
    num_authors = Author.objects.count()

    # Papildome kintamuoju num_visits, įkeliame jį į kontekstą.
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1

    # perduodame informaciją į šabloną žodyno pavidale:
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
    }

    # renderiname index.html, su duomenimis kintamąjame context
    return render(request, 'index.html', context=context)


def authors(request):
    paginator = Paginator(Author.objects.all(), 2)
    page_number = request.GET.get('page')
    paged_authors = paginator.get_page(page_number)
    context = {
        'authors': authors
    }
    #print(authors)
    return render(request, 'authors.html', context=context)

def author(request, author_id):
    single_author = get_object_or_404(Author, pk=author_id)
    #pk > primary key
    return render(request, 'author.html', {'author': single_author})
#------function based views.



#class based views:
class BookListView(ListView):
    model = Book
    paginate_by = 2
    template_name = 'book_list.html'


class BookDetailView(DetailView):
    model = Book
    template_name = 'book_detail.html'
    form_class = BookReviewForm

    class Meta:
        ordering = ['title']

    # nurodome, kur atsidursime komentaro sėkmės atveju.
    def get_success_url(self):
        return reverse('book-detail', kwargs={'pk': self.object.id})

    # įtraukiame formą į kontekstą, inicijuojame pradinę 'book' reikšmę.
    def get_context_data(self, *args, **kwargs):
        context = super(BookDetailView, self).get_context_data(**kwargs)
        context['form'] = BookReviewForm(initial={'book': self.object})
        return context

    # standartinis post metodo perrašymas, naudojant FormMixin, galite kopijuoti tiesiai į savo projektą.
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    # štai čia nurodome, kad knyga bus būtent ta, po kuria komentuojame, o vartotojas bus tas, kuris yra prisijungęs.
    def form_valid(self, form):
        form.instance.book = self.object
        form.instance.reviewer = self.request.user
        form.save()
        return super(BookDetailView, self).form_valid(form)




class LoanedBooksByUserListView(LoginRequiredMixin, ListView):
    model = BookInstance
    context_object_name = 'books'
    template_name = 'user_books.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(reader=self.request.user).order_by('due_back')


#-------------class based views.

class BookByUserDetailView(LoginRequiredMixin, DetailView):
    model = BookInstance
    template_name = 'user_book.html'


class BookByUserCreateView(LoginRequiredMixin, CreateView):
    model = BookInstance
    fields = ['book', 'due_back']
    success_url = "/library/mybooks/"
    template_name = 'user_book_form.html'

    def form_valid(self, form):
        form.instance.reader = self.request.user
        return super().form_valid(form)


class BookByUserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = BookInstance
    fields = ['book', 'due_back']
    success_url = "/library/mybooks/"
    template_name = 'user_book_form.html'

    def form_valid(self, form):
        form.instance.reader = self.request.user
        return super().form_valid(form)

    def test_func(self):
        book = self.get_object()
        return self.request.user == book.reader


class BookByUserDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = BookInstance
    success_url = "/library/mybooks/"
    template_name = 'user_book_delete.html'

    def test_func(self):
        book = self.get_object()
        return self.request.user == book.reader



def search(request):
    """
    paprasta paieška. query ima informaciją iš paieškos laukelio,
    search_results prafiltruoja pagal įvestą tekstą knygų pavadinimus ir aprašymus.
    Icontains nuo contains skiriasi tuo, kad icontains ignoruoja ar raidės
    didžiosios/mažosios.
    """
    query = request.GET.get('query')
    search_results = Book.objects.filter(Q(title__icontains=query) | Q(summary__icontains=query))
    return render(request, 'search.html', {'books': search_results, 'query': query})


#registracijos funkcija:
@csrf_protect
def register(request):
    if request.method == "POST":
        # pasiimame reikšmes iš registracijos formos
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        # tikriname, ar sutampa slaptažodžiai
        if password == password2:
            # tikriname, ar neužimtas username
            if User.objects.filter(username=username).exists():
                messages.error(request, _(f'Username {username} already exists!'))
                return redirect('register')
            else:
                # tikriname, ar nėra tokio pat email
                if User.objects.filter(email=email).exists():
                    messages.error(request, _(f'Email {email} already exists!'))
                    return redirect('register')
                else:
                    # jeigu viskas tvarkoje, sukuriame naują vartotoją
                    User.objects.create_user(username=username, email=email, password=password)
        else:
            messages.error(request, _('Passwords do not match!'))
            return redirect('register')
    return render(request, 'register.html')


@login_required
def profilis(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfilisUpdateForm(request.POST, request.FILES, instance=request.user.profilis)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, _(f"Profile has been updated"))
            return redirect('profilis')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfilisUpdateForm(instance=request.user.profilis)

    context = {
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'profilis.html', context)