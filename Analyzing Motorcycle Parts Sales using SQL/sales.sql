CREATE TABLE sales (
	order_number VARCHAR(10) PRIMARY KEY,
	date DATE,
	warehouse VARCHAR (10),
	client_type VARCHAR(20),
	product_line VARCHAR(255),
	quantity  INTEGER,
	unit_price NUMERIC(6,2),
	total NUMERIC(6,2),
	payment VARCHAR(20),
	payment_fee NUMERIC(6,2)
)