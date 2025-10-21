from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome_page, name='welcome'),
    path('404/',views.page_404,name='404'),
    path('student_view/',views.student_book_view,name='non_user'),
    path('login/', views.superuser_login, name='superuser_login'),
    path('logout/', views.superuser_logout, name='superuser_logout'),
    path('notices/', views.notices_view, name='notices'),
    path('dashboard/',views.dash_view,name='dash'),
    path('notice/delete/<int:notice_id>/', views.delete_notice_view, name='delete_notice'),
    path('add_notice/', views.add_notice_view, name='add_notice'),
    path('books/', views.book_list_view, name='book_list_view'),
    path('books/<int:pk>/', views.book_detail_view, name='book_detail_view'),
    path('books/add/', views.add_new_book, name='add_new_book'),
    path('books/<int:pk>/delete/', views.book_delete, name='book_delete'),
    path('students/', views.student_list_view, name='student_list_view'),
    path('students/<int:pk>/', views.student_detail_view, name='student_detail_view'),
    path('students/add_borrow/', views.add_student_and_borrow, name='add_student_and_borrow'),
    path('return/<int:pk>/', views.return_book, name='return_book'),
    path('search/books/', views.search_book, name='search_book'),
    path('search/students/', views.search_student, name='search_student'),
    path('book_requested/',views.book_requested,name='book_requested'),
    path('book_requested/<int:pk>/approve/', views.approve_request, name='approve_request'),
    path('book_requested/<int:pk>/deny/', views.deny_request, name='deny_request'),
    path('confirm_return/<int:pk>/', views.confirm_return_view, name='confirm_return'),
    
]

