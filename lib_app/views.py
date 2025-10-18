from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from datetime import date, datetime
import re
from django.utils import timezone
from .models import Book, Student, Borrower, Notice
from django.contrib.auth.models import User
# ---------- Public / Non-authenticated views ----------

def welcome_page(request):
    if request.user.is_superuser:
        return redirect('dash')
    return render(request, 'books/welcome.html')
def student_book_view(request):
    notices = Notice.objects.all().order_by('-created_at')
    query = request.GET.get('q', '').strip()

    if query:
        all_books = Book.objects.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(summary__icontains=query)
        ).order_by('title')
    else:
        all_books = Book.objects.all().order_by('title')

    context = {
        'books': all_books,
        'notices': notices,
        'query': query,
    }
    return render(request, 'student/non_user.html', context)


def page_404(request):
    return render(request,'404.html')
@login_required
def dash_view(request):
    total_books = Book.objects.count()
    total_borrowers = Student.objects.filter(borrower__isnull=False).distinct().count()
    total_lent_books = Borrower.objects.count()
    overdue_books = Borrower.objects.filter(return_date__lt=date.today()).count()
    current_time = timezone.now()

    context = {
        'total_books': total_books,
        'total_borrowers': total_borrowers,
        'total_lent_books': total_lent_books,
        'overdue_books': overdue_books,
        'current_time': current_time,
    }
    return render(request, 'books/dashboard.html', context)   
@login_required
def add_notice_view(request):
    if request.method == "POST" and request.user.is_superuser:
        title = request.POST['title']
        message = request.POST['message']
        Notice.objects.create(title=title, message=message, posted_by=request.user)
    return redirect('notices')

def notices_view(request):
    notices = Notice.objects.all().order_by('-created_at')  
    return render(request, 'books/notices.html', {'notices': notices})

@login_required
def delete_notice_view(request, notice_id):
    if request.user.is_superuser:
        notice = get_object_or_404(Notice, id=notice_id)
        notice.delete()
    return redirect('notices')

def superuser_login(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('book_list_view')
        else:
            messages.error(request, "You are not authorized.")
            return redirect('welcome')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_superuser:
                login(request, user)
                return redirect('book_list_view')
            else:
                messages.error(request, "You are not authorized to log in here.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'administrator/login.html')



@login_required
def superuser_logout(request):
    logout(request)
    return redirect('welcome')


@login_required
def book_list_view(request):
    books = Book.objects.all()
    num_books = Book.objects.all().count()
    students = Student.objects.filter(borrower__isnull=False).distinct()
    num_borrowers = students.count()
    return render(request, 'books/book_list.html', {
        'book_list': books,
        'logged_in': request.user.username,
        ' num_books': num_books,
        'num_borrowers':num_borrowers,
    })

@login_required
def add_new_book(request):
    if not request.user.is_superuser:
        return redirect('index')
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        summary = request.POST.get('summary')
        isbn = request.POST.get('isbn')
        cover_image=request.FILES.get('cover_image')
        pdf_file = request.FILES.get('pdf_file')
        copies = int(request.POST.get('available_copies', 0))

        if title and author and copies > 0:
            Book.objects.create(
                title=title, author=author, summary=summary,
                isbn=isbn, total_copies=copies, available_copies=copies,cover_image=cover_image,
                pdf_file=pdf_file
            )
            return render(request, 'books/result.html', {
                'message': f"✅ Book '{title}' added successfully!"
            })
    return render(request, 'books/add_book.html')

@login_required
def book_detail_view(request, pk):
    book = get_object_or_404(Book, id=pk)
    student = Student.objects.filter(roll_no=request.user).first()
    return render(request, 'books/book_detail.html', {'book': book, 'student': student})



@login_required
def book_delete(request, pk):
    if not request.user.is_superuser:
        return redirect('index')
    book = get_object_or_404(Book, pk=pk)
    book.delete()
    return redirect('book_list_view')

# ---------- Students ----------

@login_required
def student_list_view(request):
    students = Student.objects.filter(borrower__isnull=False).distinct()
    num_borrowers = students.count()
    return render(request, 'books/student_list.html', {'students': students,'num_borrowers':num_borrowers})

@login_required
def student_detail_view(request, pk):
    student = get_object_or_404(Student, id=pk)
    librarian=request.user.username
    message = f"Hello {student.name},This is the Hope Haven Secondary School Librarian ,Mr {librarian} i inform you that \n\n you have an overdue book. Please return them as soon as possible or you get fined.\n\nThank you."
    books = Borrower.objects.filter(student=student)
    return render(request, 'books/student_detail.html', {'student': student, 'books': books,'message':message})

@login_required
def student_create(request):
    if not request.user.is_superuser:
        return redirect('index')
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('student_list_view')
    else:
        form = StudentForm()
    return render(request, 'books/form.html', {'form': form})

@login_required
def student_update(request, pk):
    if not request.user.is_superuser:
        return redirect('index')
    student = get_object_or_404(Student, id=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_list_view')
    else:
        form = StudentForm(instance=student)
    return render(request, 'books/form.html', {'form': form})

@login_required
def add_student_and_borrow(request):
    if not request.user.is_superuser:
        return redirect('index')
    books = Book.objects.filter(available_copies__gt=0)
    if request.method == 'POST':
        roll_no = request.POST.get('roll_no')
        name = request.POST.get('name')
        email = request.POST.get('email')
        book_ids = request.POST.getlist('books')
        return_date = request.POST.get('return_date')
        fine = request.POST.get('fine')
        student, created = Student.objects.get_or_create(
            email=email, defaults={'roll_no': roll_no, 'name': name, 'total_books_due': 0})
        if not created:
            student.name = name
            student.roll_no = roll_no
            student.save()
        issued_count = 0
        for book_id in book_ids:
            book = get_object_or_404(Book, id=book_id)
            if book.available_copies > 0 and student.total_books_due < 10:
                Borrower.objects.create(
                    student=student, book=book,
                    issue_date=datetime.now(),
                    return_date=return_date,
                    fine=fine
                )
                book.available_copies -= 1
                student.total_books_due += 1
                book.save()
                student.save()
                issued_count += 1
        return render(request, 'books/result.html', {
            'message': f"✅ {issued_count} book assigned to {student.name}."
        })
    return render(request, 'books/add_student.html', {'books': books})

@login_required
def student_delete(request, pk):
    if not request.user.is_superuser:
        return redirect('index')
    student = get_object_or_404(Student, pk=pk)
    student.delete()
    return redirect('student_list_view')

@login_required
def confirm_return_view(request, pk):
    borrower = get_object_or_404(Borrower, id=pk)
    if request.method == "GET":
        return render(request, "books/confirm_return.html", {"borrower": borrower})
    if request.method == "POST":
        student = borrower.student
        book = borrower.book
        student.total_books_due -= 1
        student.save()
        book.available_copies += 1
        book.save()
        borrower.delete()
        return redirect("student_list_view")

# ---------- Search Helpers ----------

def normalize_query(query_string, findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]

def get_query(query_string, search_fields):
    query = None
    for term in normalize_query(query_string):
        or_query = None
        for field in search_fields:
            q = Q(**{f"{field}__icontains": term})
            or_query = q if or_query is None else or_query | q
        query = or_query if query is None else query & or_query
    return query

@login_required
def search_book(request):
    query_string = request.GET.get('q', '').strip()
    if query_string:
        q_obj = get_query(query_string, ['title', 'summary', 'author'])
        books = Book.objects.filter(q_obj).distinct()
    else:
        books = Book.objects.all()
    return render(request, 'books/book_list.html', {
        'book_list': books,
        'query': query_string,
        'logged_in': request.user.username
    })

@login_required
def search_student(request):
    query_string = request.GET.get('q', '').strip()
    students = Student.objects.filter(get_query(query_string, ['roll_no', 'name', 'email'])) if query_string else Student.objects.all()
    return render(request, 'books/student_list.html', {'students': students, 'query': query_string})
