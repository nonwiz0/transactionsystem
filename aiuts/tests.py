from django.test import TestCase
from .models import Transaction, User
from django.urls import reverse

# Create your tests here.
class UserRegistrationTest(TestCase):
    def test_registration_with_all_information(self):
        """
        This testing to see whether the signing up works when all the information is provided
        """
        response = self.client.post(reverse('aiuts:create_acc'), {"fullname": "Testing01", "password": "Asd,car15"}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "afe600a43cea6bdaf6c362905db6b883 has been created!")
    
    def test_registration_bypass_fullname(self):
        """
        This testing is checking the response of the backend when the required part of the fullname is bypass. To see whether the system will
        accept with the blank full name or not.
        """
        response = self.client.post(reverse('aiuts:create_acc'), {"fullname": "", "password": "Asd,car15"}, follow=True)
        self.assertEqual(response.status_code, 200)
        blank_fullname = User.objects.filter(pk="d41d8cd98f00b204e9800998ecf8427e").exists()
        self.assertEqual(False, blank_fullname)
 
    def test_registration_bypass_password(self):
        """
        Like the previous test, but this one is to check the password.
        """
        response = self.client.post(reverse('aiuts:create_acc'), {"fullname": "Testing01", "password": ""}, follow=True)
        self.assertEqual(response.status_code, 200)
        if User.objects.filter(pk="afe600a43cea6bdaf6c362905db6b883").exists():
            blank_password = User.objects.get(pk="afe600a43cea6bdaf6c362905db6b883").password == 'd41d8cd98f00b204e9800998ecf8427e'
            self.assertEqual(False, blank_password)
 
    def test_registration_bypass_blank_both(self):
        """
        This testing is the combination of both bypassing full name and password.
        """
        response = self.client.post(reverse('aiuts:create_acc'), {"fullname": "", "password": ""}, follow=True)
        self.assertEqual(response.status_code, 200)
        blank_fullname = User.objects.filter(pk="d41d8cd98f00b204e9800998ecf8427e").exists()
        if blank_fullname:
            blank_password = User.objects.get(pk="d41d8cd98f00b204e9800998ecf8427e").password == 'd41d8cd98f00b204e9800998ecf8427e'
            blank_both = blank_fullname == blank_password
            self.assertEqual(False, blank_both)



class UserCheckBalanceTest(TestCase):
    def test_check_balance_with_detail(self):
        """
        This testing is to check the balance to see whether it can appear out properly or not. We proceed first by creating an account, then next, we can check the balance.
        """
        response = self.client.post(reverse('aiuts:create_acc'), {"fullname": "Testing01", "password": "Asd,car15"}, follow=True)
        response = self.client.post(reverse('aiuts:checkbalance'), {"acc_id": "afe600a43cea6bdaf6c362905db6b883", "password":"Asd,car15"}, follow=True)
        self.assertContains(response, "Your account has")

    def test_check_balance_with_no_acc_id(self):
        """
        The test purpose is to check whether the server accepting whitespace for the acc_id or not. We got an issue at first because our function didn't return 
        an appropriate message / page, so we fixed the code by returning an appripriate response or page
        """
        response = self.client.post(reverse('aiuts:create_acc'), {"fullname": "Testing01", "password": "Asd,car15"}, follow=True)
        response = self.client.post(reverse('aiuts:checkbalance'), {"acc_id": "", "password":"Asd,car15"}, follow=True)
        self.assertEqual(response.status_code, 200)
    
    def test_check_balance_with_no_pass(self):
        """
        Test case with unprovided password eventhough the acc_id is provided. The same solution as the function above.
        """
        response = self.client.post(reverse('aiuts:create_acc'), {"fullname": "Testing01", "password": "Asd,car15"}, follow=True)
        response = self.client.post(reverse('aiuts:checkbalance'), {"acc_id": "afe600a43cea6bdaf6c362905db6b883", "password":""}, follow=True)
        self.assertEqual(response.status_code, 200)
    
    def test_check_balance_with_no_id_pw(self):
        """
        The same test case when there is no acc_id and pw, it is fixed after we fixed the no_acc_id
        """
        response = self.client.post(reverse('aiuts:create_acc'), {"fullname": "Testing01", "password": "Asd,car15"}, follow=True)
        response = self.client.post(reverse('aiuts:checkbalance'), {"acc_id": "", "password":""}, follow=True)
        self.assertEqual(response.status_code, 200)
    
    def test_check_balance_with_non_existing_id(self):    
        """
        Test case when the id is not provided. Fix by the previous solution.
        """
        response = self.client.post(reverse('aiuts:checkbalance'), {"acc_id": "adsfawefuihewifhui23123412", "password":"asdf2323"}, follow=True)
        self.assertEqual(response.status_code, 200)
    
class UserSendMoneyTest(TestCase):
    def test_send_money_acc_with_detail(self):
        """
        This test case to send money to another acc. We starts with creating two samples acc, one as a sender and another as a receiver. Then we can start sending and we confirm it by checking whether the receiver get more money than before the sending or not.
        """
        password = "Asd,car15"
        self.client.post(reverse('aiuts:create_acc'), {"fullname": "Testing01", "password": password}, follow=True)
        self.client.post(reverse('aiuts:create_acc'), {"fullname": "Testing02", "password": password}, follow=True)
        acc_1_id = "afe600a43cea6bdaf6c362905db6b883"
        acc_1_balance = float(User.objects.get(pk=acc_1_id).balance)
        acc_2_id = "1501b35612484ab78d6e6c5e52ba1328"
        curr_acc_2_balance = float(User.objects.get(pk=acc_2_id).balance)
        response = self.client.post(reverse('aiuts:sendmoney'), {"source": acc_1_id, "destination": acc_2_id, "amount": acc_1_balance / 2, "password": password, "remark": "Test sending money from first account to the second acc" }, follow=True)
        acc_2_get_more_money = User.objects.get(pk=acc_2_id).balance > curr_acc_2_balance
        self.assertEqual(True, acc_2_get_more_money)
    
    def test_send_money_acc_to_its_own_acc(self):
        """
        The test purpose here to prevent one acc sending money to its own acc that might lost the money in certain result.
        """
        password = "Asd,car15"
        self.client.post(reverse('aiuts:create_acc'), {"fullname": "Testing01", "password": password}, follow=True)
        acc_1_id = "afe600a43cea6bdaf6c362905db6b883"
        curr_acc_1_balance = User.objects.get(pk=acc_1_id).balance
        response = self.client.post(reverse('aiuts:sendmoney'), {"source": acc_1_id, "destination": acc_1_id, "amount": curr_acc_1_balance / 2, "password": password, "remark": "Test sending money from first account to the its own acc" }, follow=True)
        after_send_balance = User.objects.get(pk=acc_1_id).balance
        acc_1_has_the_same_amount = User.objects.get(pk=acc_1_id).balance == curr_acc_1_balance
        self.assertEqual(True, acc_1_has_the_same_amount)
    
    def test_send_negative_amount_money_acc_with_detail(self):
        """
        This testing to counter the the ammount can be hacked to be negative in which can negate and make the sender money to increase instead. 
        """
        password = "Asd,car15"
        self.client.post(reverse('aiuts:create_acc'), {"fullname": "Testing01", "password": password}, follow=True)
        acc_1_id = "afe600a43cea6bdaf6c362905db6b883"
        curr_acc_1_balance = User.objects.get(pk=acc_1_id).balance
        response = self.client.post(reverse('aiuts:sendmoney'), {"source": acc_1_id, "destination": acc_1_id, "amount": -curr_acc_1_balance, "password": password, "remark": "Test sending money from first account to the its own acc" }, follow=True)
        acc_1_has_the_same_amount = User.objects.get(pk=acc_1_id).balance == curr_acc_1_balance
        self.assertEqual(True, acc_1_has_the_same_amount)
   
    def test_send_insufficient_money_acc_with_detail(self):
        """
        This test to make sure that user have enough money first to send
        """
        password = "Asd,car15"
        self.client.post(reverse('aiuts:create_acc'), {"fullname": "Testing01", "password": password}, follow=True)
        acc_1_id = "afe600a43cea6bdaf6c362905db6b883"
        curr_acc_1_balance = User.objects.get(pk=acc_1_id).balance
        response = self.client.post(reverse('aiuts:sendmoney'), {"source": acc_1_id, "destination": acc_1_id, "amount": curr_acc_1_balance * 2, "password": password, "remark": "Test sending money from first account to the its own acc" }, follow=True)
        acc_1_has_the_same_amount = User.objects.get(pk=acc_1_id).balance == curr_acc_1_balance
        self.assertEqual(True, acc_1_has_the_same_amount)
   
    def test_send_money_acc_with_incorrect_pw(self):
        """
        This test is to cancel users action when entered wrong pw
        """
        password = "Asd,car15"
        wrong_pass = "Aasdfasdf"
        self.client.post(reverse('aiuts:create_acc'), {"fullname": "Testing01", "password": password}, follow=True)
        self.client.post(reverse('aiuts:create_acc'), {"fullname": "Testing02", "password": password}, follow=True)
        acc_1_id = "afe600a43cea6bdaf6c362905db6b883"
        curr_acc_1_balance = User.objects.get(pk=acc_1_id).balance
        acc_2_id = "1501b35612484ab78d6e6c5e52ba1328"
        curr_acc_2_balance = User.objects.get(pk=acc_2_id).balance
        response = self.client.post(reverse('aiuts:sendmoney'), {"source": acc_1_id, "destination": acc_2_id, "amount": curr_acc_1_balance / 2, "password": wrong_pass, "remark": "Test sending money from first account to the second acc" }, follow=True)
        acc_2_get_more_money = User.objects.get(pk=acc_2_id).balance > curr_acc_2_balance
        # Expected to be false because the password is incorrect
        self.assertEqual(False, acc_2_get_more_money)
    
    def test_send_money_acc_with_nonexisting_recipient(self):
        """
        This test to find whether the money will gone to nonexisting recipient or not.
        """
        password = "Asd,car15"
        self.client.post(reverse('aiuts:create_acc'), {"fullname": "Testing01", "password": password}, follow=True)
        acc_1_id = "afe600a43cea6bdaf6c362905db6b883"
        acc_1_balance = User.objects.get(pk=acc_1_id).balance
        response = self.client.post(reverse('aiuts:sendmoney'), {"source": acc_1_id, "destination": "fasdfawefhaweiufhuiew", "amount": acc_1_balance / 2, "password": password, "remark": "Test sending money from first account to the second acc" }, follow=True)
        acc_balance_remain_the_same = User.objects.get(pk=acc_1_id).balance == acc_1_balance
        self.assertEqual(True, acc_balance_remain_the_same)
    
    def test_send_money_acc_with_incorrect_acc_id(self):
        """
        Checking whether the incorrect or different acc_id as sender will work
        """
        password = "Asd,car15"
        self.client.post(reverse('aiuts:create_acc'), {"fullname": "Testing01", "password": password}, follow=True)
        self.client.post(reverse('aiuts:create_acc'), {"fullname": "Testing02", "password": password}, follow=True)
        acc_1_id = "afe600a43cea6bdaf6c362905db6b883"
        acc_1_balance = User.objects.get(pk=acc_1_id).balance
        acc_2_id = "1501b35612484ab78d6e6c5e52ba1328"
        curr_acc_2_balance = User.objects.get(pk=acc_2_id).balance
        response = self.client.post(reverse('aiuts:sendmoney'), {"source": "erhsifrjiuer", "destination": acc_2_id, "amount": acc_1_balance / 2, "password": password, "remark": "Test sending money from first account to the second acc" }, follow=True)
        self.assertEqual(response.status_code, 200)

class UserSummaryTransactionTest(TestCase):
    def test_summary_transaction_with_detail(self):
        """
        To see or check whether the summary is working well displaying the records
        """
        password = "Asd,car15"
        remark = "Test sending money from first account to the second acc"
        self.client.post(reverse('aiuts:create_acc'), {"fullname": "Testing01", "password": password}, follow=True)
        self.client.post(reverse('aiuts:create_acc'), {"fullname": "Testing02", "password": password}, follow=True)
        acc_1_id = "afe600a43cea6bdaf6c362905db6b883"
        acc_1_balance = User.objects.get(pk=acc_1_id).balance
        acc_2_id = "1501b35612484ab78d6e6c5e52ba1328"
        curr_acc_2_balance = User.objects.get(pk=acc_2_id).balance
        self.client.post(reverse('aiuts:sendmoney'), {"source": acc_1_id, "destination": acc_2_id, "amount": acc_1_balance / 2, "password": password, "remark": remark }, follow=True)
        acc_2_get_more_money = float(User.objects.get(pk=acc_2_id).balance)
        amount_receive = "{:.2f}".format(acc_2_get_more_money)
        response = self.client.post(reverse('aiuts:getsummaryoftransaction'), {"acc_id": acc_1_id, "password": password}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You")
        self.assertContains(response, remark)


        
    
    

    
    
        
