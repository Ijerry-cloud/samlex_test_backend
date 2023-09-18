select * from etl_pipelines_etftransaction;

select transaction_status, count(*) from etl_pipelines_etftransaction GROUP by transaction_status;

select * from etl_pipelines_etftransaction, jsonb_array_elements(data) elems where debit_response like '%insufficient%';
select
    *
from
    etl_pipelines_etftransaction
where
    lower(transaction_type) like '%withdrawal%'
    and monitoring_status is null;

 -- flag any withdrawal that is more that 500,000 as suspected.
 update etl_pipelines_etftransaction 
 set monitoring_comments = monitoring_comments || '&' || 'TRANSACTION AMOUNT ABOVE 500,000'
 where lower(transaction_type) like '%withdraw%' and
 monitoring_status is null and 
 amount > 500000;
 
 -- flag any withdrawal that has carried out more that 3 transactions on a single card.
 for table_record in (select response->>'PAN' as CARD, date(transaction_created_at) as txn_date, count(*) as TXN_VOL from etl_pipelines_etftransaction
	 where lower(transaction_type) like '%withdraw%' and
	 monitoring_status is null
	 group by response->>'PAN', date(transaction_created_at)
	 having count(*) > 3;)
	 loop
 		
 		update etl_pipelines_etftransaction 
 		set monitoring_comments = monitoring_comments || '&' || 'EXCEEDED 3 TRANSACTIONS: ' || table_record.txn_vol || ' DISCOVERED FOR ' || table_record.card || ' on ' || table_record.txn_vol 
 		where response->>'PAN' = table_record.card and date(transaction_created_at) = table_record.txn_date;
 		
	 end loop;
	 
-- flag any account that has made more than 5 million transactions daily limit
for table_record in (select account, date(transaction_created_at) as txn_date, sum(amount) as txn_val from etl_pipelines_etftransaction 
where lower(transaction_type) like '%transfer%'
and monitoring_status is null
group by account, date(transaction_created_at)
having sum(amount) > 5000000):
	loop
		update etl_pipelines_etftransaction
		set monitoring_comments = monitoring_comments || '&' || 'DAILY LIMIT OF 5,000,000 EXCEEDED ON ACCOUNT: ' || table_record.account || ' , CURRENT AMOUNT ' || sum(amount) || ' ON DATE: ' || table_record.txn_date 
 		where account = table_record.account and date(transaction_created_at) = table_record.txn_date;
end loop;
	
-- flag any transfer transaction which exceeds 500,000

update etl_pipelines_etftransaction 
set monitoring_comments = monitoring_comments || '&' || 'EXCEEDED SINGLE TRANSFER LIMIT OF 500,000'
where amount > 500000 and 
lower(transaction_type) like '%transfer%';

-- flag duplicate transfers into same account number and name combinations after 3 attempts


-- flag any user trying to transfer above thier limit after 3 attempts in the same day.



--- flag any user trying to transfer above thier wallet balance after 3 times.
for table_record in (select wallet_id, date(transaction_created_at) as txn_date, count(*) as txn_count from etl_pipelines_etftransaction 
where monitoring_status is null and 
lower(transaction_type) like '%transfer%' and 
lower(debit_response->>'message') like '%ins%'
group by wallet_id, date(transaction_created_at))
having count(*) > 3:
	loop
		update etl_pipelines_etftransaction
		set monitoring_comments = monitoring_comments || '&' || 'USER WITH WALLET ID: ' || table_record.wallet_id || ' TRANSFERRING ABOVE THIER LIMITS ' || table_record.txn_count || ' TIMES, ON DATE: ' || table_record.txn_date 
 		where wallet_id = table_record.wallet_id and date(transaction_created_at) = table_record.txn_date;
end loop;




 
 -- 
 
 select wallet_id, count(*) from etl_pipelines_etftransaction 
 where lower(debit_response->>'message') like '%ins%'
 group by wallet_id;
 
 
 
/**
*
*
most likely fields of interest in the the etf transaction table

transaction type - ['airtime', 'transfer', 'withdrawal', 'electricity', 'data', 'cable']
account - input field
account_type - [api for this fields]
wallet id - input field
channel - [api for this field]
reference - input field
transaction status - [successful, validation, failed, pending]
reversal - [true, false]
credit status - [true, false0]
payment method - []
description - 
monitoring_status - [suspected, cleared]
monitoring_comments - %%
product - []
provider - [ tms, capricorn, nibss ] api

*
**/


{"MTI": "0200", "PAN": "418745XXXXXX4779", "rrn": "167056888483", "STAN": "563006", "amount": 100, "channel": "linuxpos", "authCode": "883828", "reversal": false, "merchantId": "2302BA000009611", "terminalId": "2SPL0011", "description": "Approved", "merchantName": "SPOUT PAYMENT INTERNAT", "responseCode": "00", "merchantAddress": "ONAL LIMITED     ", "transactionTime": "2022-12-09 06:40:52", "responseDescription": "Approved"}


{"reference": "6399984fb8549fea4c63deaa", "statusCode": "0", "baxiReference": "6399984fb8549fea4c63deaa", "provider_message": "Airtime Topup successful on 08112681154", "transactionStatus": "success", "transactionMessage": "Airtime Topup successful on 08112681154", "transactionReference": "6399984fb8549fea4c63deaa"}


{"amount": 100, "narration": "transfer payment", "sessionID": "999999221020201826735003964857", "channelCode": 1, "responseCode": "00", "transactionId": "000076221020191825683471420634", "nameEnquiryRef": "999999221020201826735003964857", "paymentReference": "NIPMINI/000076221020191825683471420634/VASTRA1837160201666293474662", "originatorKYCLevel": "1", "beneficiaryKYCLevel": "1", "transactionLocation": "1.38716,3.05117", "originatorAccountName": "vee Test", "beneficiaryAccountName": "vee Test", "originatorAccountNumber": "0112345678", "beneficiaryAccountNumber": "0112345678", "destinationInstitutionCode": "999998", "originatorBankVerificationNumber": "33333333333", "beneficiaryBankVerificationNumber": "33333333332"}
 
 select credit_status,  count(*) from etl_pipelines_etftransaction group by credit_status; 
 