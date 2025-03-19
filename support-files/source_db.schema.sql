--
-- PostgreSQL database source_db
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);

-- Name: product; Type: TABLE; Schema: public; Owner: source_db

CREATE TABLE public.product (
    product_id VARCHAR(36) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    brand_name VARCHAR(100),
    category VARCHAR(50) NOT NULL,
    price INT,
    promotion_price INT NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL
);

ALTER TABLE public.product OWNER TO source_db;

-- Name: customer; Type: TABLE; Schema: public; Owner: source_db

CREATE TABLE public.customer (
    customer_id VARCHAR(36) PRIMARY KEY,
    customer_name VARCHAR(50) NOT NULL,
    gender VARCHAR(10) NOT NULL,
    birth DATE NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone_number VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL,
    registered_at DATE NOT NULL
);

ALTER TABLE public.customer OWNER TO source_db;

-- Name: customer_behavior; Type: TABLE; Schema: public; Owner: source_db

CREATE TABLE public.customer_behavior (
    customer_id VARCHAR(36) NOT NULL,
    product_id VARCHAR(36) NOT NULL,
    action_type VARCHAR(20) NOT NULL,
    device_type VARCHAR(20) NOT NULL,
    referrer VARCHAR(20) NOT NULL,
    action_at TIMESTAMPTZ NOT NULL,

    PRIMARY KEY (customer_id, product_id, action_at)
);

ALTER TABLE public.customer_behavior OWNER TO source_db;

-- Name: transaction; Type: TABLE; Schema: public; Owner: source_db

CREATE TABLE public.transaction (
    customer_id VARCHAR(36) NOT NULL,
    product_id VARCHAR(36) NOT NULL,
    quantity INT NOT NULL,
    promotion_price INT NOT NULL,
    amount INT NOT NULL,
    discount INT DEFAULT 0,
    gift VARCHAR(100),
    total INT NOT NULL,
    transaction_at TIMESTAMPTZ NOT NULL,

    PRIMARY KEY (customer_id, product_id, transaction_at)
    
);

ALTER TABLE public.transaction OWNER TO source_db;

-- Name: promotion_date; Type: TABLE; Schema: public; Owner: source_db

CREATE TABLE public.promotion_date (
    day_of_week INT NOT NULL,
    promotion_type VARCHAR(20) NOT NULL,
    published_at TIMESTAMPTZ NOT NULL,

    PRIMARY KEY (day_of_week, published_at)
);

ALTER TABLE public.promotion_date OWNER TO source_db;

INSERT INTO public.promotion_date (day_of_week, promotion_type, published_at)
VALUES
    (0, '滿額折扣', '2024-01-01'),
    (1, '多件優惠', '2024-01-01'),
    (2, '多件優惠', '2024-01-01'),
    (3, '多件優惠', '2024-01-01'),
    (4, '滿額折扣', '2024-01-01'),
    (5, '免運滿額贈', '2024-01-01'),
    (6, '免運滿額贈', '2024-01-01');

-- Name: promotion; Type: TABLE; Schema: public; Owner: source_db

CREATE TABLE public.promotion (
    promotion_id SERIAL PRIMARY KEY,
    promotion_name VARCHAR(50) NOT NULL,
    promotion_type VARCHAR(20) NOT NULL,
    cash_threshold INT, 
    quantity_threshold INT,
    discount_rate FLOAT,
    gift VARCHAR(20),
    published_at TIMESTAMPTZ NOT NULL
);

ALTER TABLE public.promotion OWNER TO source_db;

INSERT INTO public.promotion (promotion_name, promotion_type, cash_threshold, quantity_threshold, discount_rate, gift, published_at)
VALUES
    ('滿1000打95折', '滿額折扣', 1000, NULL, 0.05, NULL,'2024-01-01'),
    ('滿2000打9折', '滿額折扣', 2000, NULL, 0.1, NULL,'2024-01-01'),
    ('滿3000打8折', '滿額折扣', 3000, NULL, 0.2, NULL,'2024-01-01'),
    ('500滿額贈', '免運滿額贈', 500, NULL, NULL, '餅乾50G','2024-01-01'),
    ('1000滿額贈', '免運滿額贈', 1000, NULL, NULL, '肉乾100G','2024-01-01'),
    ('2000滿額贈', '免運滿額贈', 2000, NULL, NULL, '凍乾100G','2024-01-01'),
    ('滿5件打9折', '多件優惠', NULL, 5, 0.1, NULL,'2024-01-01'),
    ('滿8件打8折', '多件優惠', NULL, 8, 0.2, NULL,'2024-01-01'),
    ('滿10件打7折', '多件優惠', NULL, 10, 0.3, NULL,'2024-01-01');
