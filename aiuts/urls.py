from django.urls import path

from . import views

app_name = 'aiuts'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('login', views.LoginView.as_view(), name='login'),
    path('login/account', views.check_account, name="checklogin"), 
    path('sign_up', views.SignupView.as_view(), name='signup'),
    path('get_balance', views.GetbalanceView.as_view(), name='getbalance'),
    path('sign_up/submit', views.create_acc, name='create_acc'),
    path('get_balance/check', views.check_balance, name="checkbalance"),
    path('get_acc_id', views.GetaccidView.as_view(), name='getaccid'),
    path('get_acc_id/check', views.check_accid, name="checkaccid"),
    path('sendmoney', views.SendMoneyView.as_view(), name='sendmoneypage' ),
    path('send_money', views.send_money, name='sendmoney'),
    path('deposit_money', views.deposit_money, name="depositmoney"),
    path('account/summary/check', views.get_summary_of_transaction, name="getsummaryoftransaction"),
    path('summary', views.TransactionView.as_view(), name='gettransaction')
]
