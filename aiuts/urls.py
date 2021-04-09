from django.urls import path

from . import views

app_name = 'aiuts'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('dashboard', views.Dashboard.as_view(), name="dashboard"),
    path('sign_up', views.SignupView.as_view(), name='signup'),
    path('sign_up/submit', views.create_acc, name='create_acc'),
    path('send_money', views.send_money, name='sendmoney'),
    path('deposit_money', views.deposit_money, name="depositmoney"),
    path('account/summary/check', views.get_summary_of_transaction, name="getsummaryoftransaction"),

]
