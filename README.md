# AIUTS < Transaction System
Latest updated on April 30, by Broset, Yilin, Andreas

## Things to work on
- Ajax function on the dashboard
- Ajax feature on Top Up page, updating the balance and record automatically when the bank approve
- Ajax feature on Send/Req money

## Accounts Login:
```
# Bank Account is the one that use to approve the Top Up Request from Users
Username: bank
Password: A****15 (lab pw)
```

```
# Normal Accounts
Username: yilin
Username#2: broset
Username#3: andreas
# Same password like the above 
```

## Updated list:
- Updated AJax's alert on Top Up
- Working on Ajax
- Added 17 testings
- Provided testings description
- Fix the views
- Minor change on the template
- Added authentication
- Modify the models
- Update the views
- Update dashboard
- added the filtering transaction (which is not optimize yet)
- Added Top Up Request
- Added Request payment
- Update searching filter

## Done
- Management of user accounts: Every user will be able to access their own dashboard that allows them to send and receive AUCs, see the history of transactions, see list of pending payments, and top-up. 
- Top-up account: This function allows to a authenticated user to request AUCs to a pre-defined account in AIUTS. The AUCs are not sent to the requester until the requester pays cash to the owner of the account. The pre-defined account must belong to an authorized finance officer of AIU. 
- Request of payment: This function allows to a authenticated user to request AUCs to another AIUTS user by using their account address. The requests   of payments are listed in the charged user's dashboard.
- Search transactions: This function allows to a authenticated user to filter the history of transactions by account address and timestamp. (On the way)
