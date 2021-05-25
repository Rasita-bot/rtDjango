from django.urls import path, include

from . import views

urlpatterns = [
#function based views:
    path('', views.index, name='index'),
    path('authors/', views.authors, name='authors'),
    path('authors/<int:author_id>', views.author, name='author'),
#class based views:
    path('books', views.BookListView.as_view(), name='books'),
    path('books/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    path('search/', views.search, name='search'),
    path('register/', views.register, name='register'),
    path('profilis/', views.profilis, name='profilis'),
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
    path('mybooks/<int:pk>', views.BookByUserDetailView.as_view(), name='my-book'),
    #path('mybooks/<uuid:pk>', views.BookByUserDetailView.as_view(), name='my-book'),
    path('mybooks/new', views.BookByUserCreateView.as_view(), name='my-borrowed-new'),
    path('mybooks/<int:pk>/update', views.BookByUserUpdateView.as_view(), name='my-book-update'),
    path('mybooks/<int:pk>/delete', views.BookByUserDeleteView.as_view(), name='my-book-delete'),
    path('i18n/', include('django.conf.urls.i18n')),
]
