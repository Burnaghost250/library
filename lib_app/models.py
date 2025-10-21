from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
class Genre(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class Language(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    summary = models.TextField(max_length=1000)
    isbn = models.CharField(max_length=13)
    genre = models.ManyToManyField(Genre)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)
    total_copies = models.IntegerField()
    available_copies = models.IntegerField()
    pdf_file = models.FileField(upload_to='book_pdfs/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)
    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('book_detail_view', args=[str(self.id)])

class Student(models.Model):
    roll_no = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=10)
    branch = models.CharField(max_length=3)
    contact_no = models.CharField(max_length=10)
    total_books_due = models.IntegerField(default=0)
    email = models.EmailField(unique=True)
    pic = models.ImageField(blank=True, upload_to='profile_image')
    def __str__(self):
        return str(self.roll_no)

class Borrower(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    issue_date = models.DateTimeField(null=True, blank=True)
    return_date = models.DateTimeField(null=True, blank=True)
    fine = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    def __str__(self):
        return f"{self.student.name} borrowed {self.book.title}"
        
class Notice(models.Model):
    title = models.CharField(max_length=100)
    message = models.TextField()
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
class Book_request(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    book_name = models.CharField(max_length=100)
    any_message = models.CharField(max_length=100, blank=True, null=True)
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    def __str__(self):
        return f"{self.username} - {self.book_name}"
