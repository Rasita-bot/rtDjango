from django.contrib import admin

from .models import Author, Genre, Book, BookInstance, BookReview, Profilis



class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    readonly_fields = ('id',)
    can_delete = False
    extra = 0 # išjungia placeholder'ius


#klase sukuriame tam, kad norime pakeisti atvaizdavima:
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    inlines = [BooksInstanceInline] #apacioje nurodyti nereikia, nes cia nurodeme


class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'due_back', 'reader', 'status')
    #pagal ka filtruosime nusirodeme zemesneje eiluteje:
    list_filter = ('status', 'due_back')
    search_fields = ('id', 'book__title')
    list_editable = ('due_back', 'status')

    fieldsets = (
        (None, {
            'fields': ('book', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'reader')
        }),
    )


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'display_books')


class BookReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'date_created', 'reviewer', 'content')


admin.site.register(Book, BookAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Genre)
admin.site.register(BookInstance, BookInstanceAdmin)
admin.site.register(BookReview, BookReviewAdmin)
admin.site.register(Profilis)
