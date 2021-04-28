from .models import Transaction, Account
from django import forms
import datetime

class TopupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account', " ")
        super(TopupForm, self).__init__(*args, **kwargs)
        self.fields['sender'].choices = [(
            Account.objects.filter(acc_id='bd5af1f610a12434c9128e4a399cef8a')[0], 'bank')]
        self.fields['recipient'].choices = [(self.account[0], 'You')]
        self.fields['amount'].widget.attrs.update({
            'step': "0.01",
            'value': 0.01 ,
            'min': 0.00,

        })
        self.fields['type'].choices = [("Top Up", "Top Up")]
        self.fields['type'].widget.attrs.update({
            'value': 'Top Up',
        })
        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
            })
    class Meta:
        model = Transaction
        fields = ('sender', 'amount', 'recipient', 'type')

