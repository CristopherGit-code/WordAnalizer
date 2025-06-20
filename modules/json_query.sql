-- Filter by date
SELECT t.id,t.metadata.file_name FROM WL_Calls t WHERE json_query(metadata, '$.report_date.date()?(@ > "2018-01-01T00:00")') IS NOT NULL;
-- Filter by type
SELECT t.id,t.metadata.file_name FROM WL_Calls t WHERE json_query(metadata, '$?(@.type == "loss")') IS NOT NULL;
-- Filter by region
SELECT t.id,t.metadata.file_name FROM WL_Calls t WHERE json_query(metadata, '$?(@.regions.region == "UK")') IS NOT NULL;
-- Filter by customer
SELECT t.id,t.metadata.file_name FROM WL_Calls t WHERE json_query(metadata, '$?(@.customer == "E.ON")') IS NOT NULL;

-- COMPLEX FILTER
SELECT t.id,t.metadata.file_name FROM WL_Calls t WHERE json_query(metadata, '$?(@.type == "loss")') IS NOT NULL AND json_query(metadata, '$.report_date.date()?(@ > "2018-01-01T00:00")') IS NOT NULL;

-- Products
SELECT t.id,t.metadata.file_name FROM WL_Calls t WHERE json_query(metadata, '$?(@.products.product starts with ("H"))') IS NOT NULL;

--SELECT t.id,t.metadata.file_name FROM WL_Calls t WHERE t.id = 1;

--SELECT t.metadata.products[0] FROM WL_Calls t;
--SELECT t.metadata.file_name FROM WL_Calls t WHERE t.metadata.regions.region = 'US';

-- Search for a dictionary
--query = f"SELECT json_query(metadata, '$.{request_info}[0].string()') FROM WL_Calls"
-- Search for a value
--query = f"SELECT json_query(metadata, '$.{request_info}.string()') FROM WL_Calls"