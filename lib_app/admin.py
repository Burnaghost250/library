from django.contrib import admin
from .models import Book, Student, Borrower, Genre, Language

admin.site.register(Book)
admin.site.register(Student)
admin.site.register(Borrower)
admin.site.register(Genre)
admin.site.register(Language)

