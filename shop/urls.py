from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.handleSignUp, name='handleSignUp'),
    path('login/', views.handeLogin, name="handleLogin"),
    path('logout/', views.handleLogout, name="handleLogout"),

    path('advertise/', views.advertise, name='advertise'),
    path('about/', views.about, name='about'),

    path('contact/', views.contact, name="ContactUs"),
    path('tracker/', views.tracker, name="TrackingStatus"),
    path('search/', views.search, name="Search"),
    path('productView/<int:myid>/', views.productView, name="productView"),
    path('orderView/', views.orderView, name="orderView"),
    path('handlerequest/', views.handlerequest, name="HandleRequest"),

    path('checkout/<int:category_id>/', views.checkout, name='checkout'),


     
     path('<int:category_id>/', views.table_menu, name='table_menu'),

    path('reset_password/',
         auth_views.PasswordResetView.as_view(template_name="shop/password_reset.html"),
         name="reset_password"),

    path('reset_password_sent/',
         auth_views.PasswordResetDoneView.as_view(template_name="shop/password_reset_sent.html"),
         name="password_reset_done"),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name="shop/password_reset_form.html"),
         name="password_reset_confirm"),

    path('reset_password_complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name="shop/password_reset_done.html"),
         name="password_reset_complete"),
     
    path('update/<int:order_id>/', views.update_order, name='update_order'),
]
