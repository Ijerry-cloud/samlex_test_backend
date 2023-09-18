
/**
* This procedure runs through the etl_pipelines_transaction table
* and filters out the transaction whose transaction type is null 
* and update the transaction type column based on the information
* on the product column that is linked to the Products table.
**/


CREATE OR REPLACE PROCEDURE public.label_transactions()
 LANGUAGE plpgsql
AS $procedure$
DECLARE
p_record record;
p_transaction_type varchar(200);
begin
    
    for p_record in (select product, count(*) as product_count from etl_pipelines_etftransaction where transaction_type is null GROUP by product) loop
    
    	select product_type into p_transaction_type from etl_pipelines_product where product_name = p_record.product;
    	update etl_pipelines_etftransaction set transaction_type = p_transaction_type where transaction_type is null and lower(product) like '%' || p_record.product || '%';
    
    end loop;
    
    -- commit;
end;$procedure$

 
 