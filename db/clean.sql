delete from traveller_data where id in (select td.id from traveller_data td left join traveller_data_periods tdp on tdp.traveller_data_id = td.id where td.upload_date + interval '1 day' < now() and tdp is null);

delete from report_results where id in (select rr.id from report_results rr where rr.version_ts < (select cust.last_available_travel_history from customers cust where cust.id = rr.customer_id));

delete from employee_travel_history where id in (select ee.id from employee_travel_history ee where ee.version_ts < (select cust.last_available_travel_history from customers cust where cust.id = ee.customer_id));

vacuum verbose;
