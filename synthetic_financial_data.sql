-- Synthetic data export
-- Generated: 2026-08-04 00:36:12 UTC
-- Modified:  every customer guaranteed at least one account
--            8 accounts added for: id-37735549, id-97897752, id-37327198,
--                                   id-21558368, id-63363976, id-95927351,
--                                   id-98193671, id-39339444

-- Drop existing tables (children first)
DROP TABLE IF EXISTS "fraud_alerts";
DROP TABLE IF EXISTS "transfers";
DROP TABLE IF EXISTS "transactions";
DROP TABLE IF EXISTS "beneficiaries";
DROP TABLE IF EXISTS "accounts";
DROP TABLE IF EXISTS "customers";

-- --------------------------------------------------------
-- Table: customers
-- --------------------------------------------------------
CREATE TABLE "customers" (
    "customer_id" VARCHAR(20) PRIMARY KEY,
    "full_name" VARCHAR(150),
    "email" VARCHAR(200),
    "phone" VARCHAR(30),
    "date_of_birth" DATE,
    "address" TEXT,
    "country_code" VARCHAR(3),
    "kyc_status" VARCHAR(20),
    "risk_rating" VARCHAR(10),
    "created_at" TIMESTAMP,
    "is_active" BOOLEAN
);

INSERT INTO "customers" ("customer_id", "full_name", "email", "phone", "date_of_birth", "address", "country_code", "kyc_status", "risk_rating", "created_at", "is_active") VALUES
    ('id-22241879', 'David Moore',     'karen.miller@test.org',        '+1-489-986-9793', '2013-06-29', '6842 Main St, Ogdenville, IL',       'FR', 'PENDING',  'HIGH',   '2008-02-21', FALSE),
    ('id-37735549', 'Henry Wilson',    'maria.thomas@mail.com',        '+1-401-396-1149', '2004-01-25', '4959 Oak Ave, Capital City, CA',     'GB', 'REJECTED', 'HIGH',   '2015-07-25', FALSE),
    ('id-52464947', 'Maria Anderson',  'bob.miller@mail.com',          '+1-608-378-7693', '2006-06-22', '6277 Main St, Shelbyville, IL',      'GB', 'VERIFIED', 'HIGH',   '2009-03-08', TRUE),
    ('id-13837496', 'Olivia Jones',    'bob.smith@demo.io',            '+1-584-677-2829', '2023-05-21', '4997 Pine Rd, Shelbyville, FL',      'DE', 'REJECTED', 'LOW',    '2002-05-28', FALSE),
    ('id-97897752', 'Karen Johnson',   'carol.davis@sample.net',       '+1-361-710-1468', '2007-04-09', '9635 Main St, Ogdenville, OH',       'CA', 'PENDING',  'HIGH',   '2008-09-17', TRUE),
    ('id-34235738', 'Grace Anderson',  'alice.brown@demo.io',          '+1-569-985-3922', '2007-05-06', '8251 Maple Dr, Springfield, NC',     'AU', 'PENDING',  'MEDIUM', '2017-01-10', FALSE),
    ('id-18575426', 'Jack Thomas',     'bob.miller@demo.io',           '+1-578-850-8870', '2022-07-12', '1904 Main St, Ogdenville, OH',       'CA', 'PENDING',  'MEDIUM', '2011-05-09', FALSE),
    ('id-22948245', 'David Johnson',   'jack.brown@mail.com',          '+1-877-382-1876', '2011-02-02', '3550 Maple Dr, Springfield, GA',     'GB', 'PENDING',  'LOW',    '2024-01-18', TRUE),
    ('id-37327198', 'Maria Wilson',    'nathan.jones@test.org',        '+1-952-679-8643', '2021-01-21', '6821 Main St, Ogdenville, TX',       'CA', 'PENDING',  'HIGH',   '2019-07-02', FALSE),
    ('id-17937219', 'Grace Brown',     'david.garcia@demo.io',         '+1-989-789-9211', '2002-03-20', '2606 Maple Dr, Springfield, PA',     'DE', 'REJECTED', 'HIGH',   '2022-08-15', FALSE),
    ('id-35897343', 'David Thomas',    'eva.jackson@mail.com',         '+1-385-701-8400', '2016-11-30', '8995 Oak Ave, Ogdenville, FL',       'DE', 'PENDING',  'MEDIUM', '2005-06-16', FALSE),
    ('id-41233495', 'Iris Jackson',    'frank.thomas@example.com',     '+1-611-478-9412', '2008-12-10', '5365 Oak Ave, Springfield, IL',      'AU', 'VERIFIED', 'LOW',    '2015-10-15', FALSE),
    ('id-21558368', 'David Anderson',  'grace.wilson@sample.net',      '+1-923-458-2529', '2000-02-16', '2772 Maple Dr, Shelbyville, TX',     'DE', 'VERIFIED', 'LOW',    '2000-12-18', FALSE),
    ('id-95898841', 'Eva Garcia',      'eva.thomas@example.com',       '+1-279-461-5066', '2006-07-05', '1758 Pine Rd, Capital City, OH',     'AU', 'REJECTED', 'MEDIUM', '2000-08-06', FALSE),
    ('id-63363976', 'Iris Williams',   'grace.davis@sample.net',       '+1-651-376-1952', '2010-05-29', '8344 Oak Ave, Brockway, NC',         'SG', 'VERIFIED', 'HIGH',   '2010-10-26', FALSE),
    ('id-28944533', 'Frank Jones',     'eva.davis@demo.io',            '+1-279-881-3625', '2015-01-23', '4036 Pine Rd, Ogdenville, GA',       'CA', 'VERIFIED', 'LOW',    '2002-12-24', TRUE),
    ('id-66431666', 'Eva Taylor',      'paul.miller@sample.net',       '+1-847-901-8166', '2020-03-22', '890 Elm Blvd, Ogdenville, TX',       'CA', 'PENDING',  'LOW',    '2009-05-31', TRUE),
    ('id-95927351', 'Bob Garcia',      'maria.moore@test.org',         '+1-851-940-7455', '2023-03-22', '7076 Elm Blvd, Capital City, PA',    'US', 'VERIFIED', 'HIGH',   '2002-01-14', FALSE),
    ('id-98193671', 'Paul Jones',      'david.jones@mail.com',         '+1-357-839-4461', '2006-11-01', '3674 Main St, Shelbyville, FL',      'FR', 'VERIFIED', 'MEDIUM', '2004-06-19', FALSE),
    ('id-39339444', 'Jack Miller',     'iris.wilson@sample.net',       '+1-631-445-8900', '2019-06-14', '6498 Cedar Ln, Capital City, NY',    'AE', 'VERIFIED', 'LOW',    '2024-05-30', FALSE);

-- --------------------------------------------------------
-- Table: accounts
-- --------------------------------------------------------
-- Original 20 rows unchanged.
-- Added 8 rows (marked below) for customers with no account:
--   id-37735549, id-97897752, id-37327198, id-21558368,
--   id-63363976, id-95927351, id-98193671, id-39339444
-- --------------------------------------------------------
CREATE TABLE "accounts" (
    "account_id" INTEGER PRIMARY KEY,
    "customer_id" VARCHAR(20),
    "account_number" VARCHAR(20),
    "account_type" VARCHAR(30),
    "currency" VARCHAR(3),
    "balance" DECIMAL(18,2),
    "credit_limit" DECIMAL(18,2),
    "interest_rate" DECIMAL(18,2),
    "status" VARCHAR(20),
    "opened_at" TIMESTAMP,
    FOREIGN KEY ("customer_id") REFERENCES "customers"("customer_id")
);

INSERT INTO "accounts" ("account_id", "customer_id", "account_number", "account_type", "currency", "balance", "credit_limit", "interest_rate", "status", "opened_at") VALUES
    -- original rows --
    (8379, 'id-22948245', 'acc-a-91616825', 'CREDIT',     'AED', 365343.67, 57463.73, 15.43, 'ACTIVE',  '2009-04-26 10:05:30'),
    (5911, 'id-52464947', 'acc-b-45662665', 'LOAN',       'GBP', 231251.94,  9007.63, 19.52, 'FROZEN',  '2016-11-21 08:26:46'),
    (8396, 'id-52464947', 'acc-b-18911651', 'CREDIT',     'SGD',   3534.15, 39577.91,  1.43, 'FROZEN',  '2007-07-02 03:28:57'),
    (3889, 'id-17937219', 'acc-c-33572639', 'INVESTMENT', 'SGD', 276448.06, 70394.51,  5.57, 'ACTIVE',  '2016-12-04 13:41:28'),
    (2012, 'id-17937219', 'acc-c-35212544', 'CREDIT',     'EUR',  59438.16, 39873.97,  7.92, 'ACTIVE',  '2021-01-01 20:39:12'),
    (5263, 'id-22948245', 'acc-c-17427768', 'LOAN',       'AED', 186112.86, 38333.98, 24.28, 'DORMANT', '2005-12-12 18:24:29'),
    (3153, 'id-13837496', 'acc-a-18521985', 'INVESTMENT', 'USD', 270750.40, 83564.91,  8.57, 'DORMANT', '2003-01-24 13:24:54'),
    (5401, 'id-52464947', 'acc-c-95135929', 'CHECKING',   'GBP',  88005.17, 43443.93, 11.56, 'FROZEN',  '2019-02-21 03:05:20'),
    (4104, 'id-35897343', 'acc-c-29422278', 'CHECKING',   'USD',  73378.17, 37746.31, 10.48, 'CLOSED',  '2014-10-26 21:34:17'),
    (1377, 'id-18575426', 'acc-a-41337515', 'SAVINGS',    'AED', 387366.53, 79981.83,  8.21, 'CLOSED',  '2015-01-30 13:39:42'),
    (8245, 'id-28944533', 'acc-a-43964828', 'INVESTMENT', 'CAD', 272996.54, 51016.32, 19.58, 'DORMANT', '2007-01-01 07:58:20'),
    (9757, 'id-35897343', 'acc-b-66245677', 'SAVINGS',    'USD', 203378.76, 89676.85, 23.00, 'ACTIVE',  '2006-08-31 06:27:17'),
    (1351, 'id-18575426', 'acc-a-79582694', 'CREDIT',     'AUD',  20051.51, 48182.64, 23.94, 'FROZEN',  '2005-07-27 08:07:25'),
    (4886, 'id-22241879', 'acc-a-19164877', 'CREDIT',     'USD', 161701.50, 48239.84, 13.86, 'DORMANT', '2007-03-07 20:26:09'),
    (1273, 'id-66431666', 'acc-b-64214229', 'CHECKING',   'AED', 409277.04, 48529.65, 14.85, 'DORMANT', '2012-01-15 01:55:57'),
    (2834, 'id-13837496', 'acc-c-92371525', 'CHECKING',   'USD', 192927.27, 37998.89, 16.84, 'DORMANT', '2015-12-20 11:38:16'),
    (1778, 'id-41233495', 'acc-b-77943995', 'SAVINGS',    'CAD', 272024.12, 42818.60,  7.32, 'FROZEN',  '2020-02-15 16:10:12'),
    (9136, 'id-28944533', 'acc-c-38931347', 'LOAN',       'AED',  97813.66, 63984.60,  8.60, 'DORMANT', '2000-06-25 07:49:18'),
    (7123, 'id-34235738', 'acc-a-18972869', 'CREDIT',     'CAD', 322430.14, 28234.72, 13.58, 'FROZEN',  '2017-05-04 02:46:36'),
    (1012, 'id-95898841', 'acc-b-64244881', 'CHECKING',   'AED', 155433.88, 93795.24, 22.00, 'DORMANT', '2014-01-07 04:52:33'),
    -- added: one account per previously unaccounted customer --
    (2001, 'id-37735549', 'acc-n-11375549', 'CHECKING',   'GBP',  42000.00, 10000.00,  5.50, 'ACTIVE',  '2016-03-14 09:00:00'),
    (2002, 'id-97897752', 'acc-n-11897752', 'SAVINGS',    'CAD',  18500.75,     0.00,  2.25, 'ACTIVE',  '2009-01-22 11:30:00'),
    (2003, 'id-37327198', 'acc-n-11327198', 'CREDIT',     'USD',  95000.00, 30000.00,  9.99, 'ACTIVE',  '2019-10-05 08:15:00'),
    (2004, 'id-21558368', 'acc-n-11558368', 'INVESTMENT', 'EUR', 210000.00,     0.00,  4.10, 'ACTIVE',  '2001-07-19 14:00:00'),
    (2005, 'id-63363976', 'acc-n-11363976', 'SAVINGS',    'SGD',  33400.50,     0.00,  1.95, 'ACTIVE',  '2011-04-30 10:45:00'),
    (2006, 'id-95927351', 'acc-n-11927351', 'CHECKING',   'USD',  76800.00, 15000.00,  6.80, 'ACTIVE',  '2002-09-11 07:30:00'),
    (2007, 'id-98193671', 'acc-n-11193671', 'CREDIT',     'EUR',  54200.00, 20000.00,  8.45, 'ACTIVE',  '2005-02-28 16:00:00'),
    (2008, 'id-39339444', 'acc-n-11339444', 'SAVINGS',    'AED',  12750.25,     0.00,  3.30, 'ACTIVE',  '2024-06-10 12:00:00');

-- --------------------------------------------------------
-- Table: beneficiaries
-- --------------------------------------------------------
CREATE TABLE "beneficiaries" (
    "beneficiary_id" VARCHAR(20) PRIMARY KEY,
    "customer_id" VARCHAR(20),
    "full_name" VARCHAR(150),
    "bank_name" VARCHAR(100),
    "account_number" VARCHAR(20),
    "routing_number" VARCHAR(15),
    "currency" VARCHAR(3),
    "country_code" VARCHAR(3),
    "is_verified" BOOLEAN,
    "created_at" TIMESTAMP,
    FOREIGN KEY ("customer_id") REFERENCES "customers"("customer_id")
);

INSERT INTO "beneficiaries" ("beneficiary_id", "customer_id", "full_name", "bank_name", "account_number", "routing_number", "currency", "country_code", "is_verified", "created_at") VALUES
    ('bid-39667694', 'id-13837496', 'Alice Miller',    'BNP Paribas',   '7443800883', '860780221', 'CAD', 'FR', FALSE, '2012-02-14 00:00:00'),
    ('bid-86482473', 'id-95898841', 'Alice Williams',  'BNP Paribas',   '1849993165', '263070186', 'AUD', 'GB', TRUE,  '2023-03-08 00:00:00'),
    ('bid-74544363', 'id-95927351', 'Maria Taylor',    'Wells Fargo',   '0929428692', '475797850', 'AUD', 'GB', FALSE, '2008-10-06 00:00:00'),
    ('bid-64722592', 'id-34235738', 'David Johnson',   'BNP Paribas',   '4203255930', '756610062', 'GBP', 'CA', TRUE,  '2008-02-14 00:00:00'),
    ('bid-84574994', 'id-18575426', 'Bob Jackson',     'Citibank',      '4617629621', '875675096', 'EUR', 'AU', TRUE,  '2019-05-28 00:00:00'),
    ('bid-75556553', 'id-37327198', 'David Johnson',   'Barclays',      '6001528732', '447301280', 'GBP', 'GB', FALSE, '2002-04-28 00:00:00'),
    ('bid-59952535', 'id-98193671', 'Bob Garcia',      'Deutsche Bank', '2125481912', '930053127', 'AUD', 'US', TRUE,  '2008-04-11 00:00:00'),
    ('bid-68544432', 'id-35897343', 'Carol Taylor',    'HSBC',          '3527781940', '766067175', 'CAD', 'US', TRUE,  '2004-02-26 00:00:00'),
    ('bid-41734247', 'id-28944533', 'Leo Johnson',     'BNP Paribas',   '6382458462', '202141943', 'EUR', 'GB', FALSE, '2018-11-26 00:00:00'),
    ('bid-51897657', 'id-95927351', 'Bob Taylor',      'Deutsche Bank', '5462117497', '012963229', 'AUD', 'CA', TRUE,  '2003-10-05 00:00:00'),
    ('bid-35747873', 'id-39339444', 'Alice Miller',    'Deutsche Bank', '3343135025', '980058101', 'CAD', 'FR', TRUE,  '2010-01-24 00:00:00'),
    ('bid-25128439', 'id-18575426', 'Frank Anderson',  'Barclays',      '5517322810', '878578334', 'USD', 'GB', FALSE, '2015-09-22 00:00:00'),
    ('bid-37732745', 'id-13837496', 'Alice Johnson',   'Chase',         '0607474975', '826624475', 'EUR', 'AU', FALSE, '2000-07-14 00:00:00'),
    ('bid-55899232', 'id-21558368', 'Leo Garcia',      'Barclays',      '3068757955', '283059379', 'USD', 'FR', FALSE, '2014-07-26 00:00:00'),
    ('bid-63439498', 'id-41233495', 'Paul Johnson',    'Chase',         '9623412408', '085712425', 'AUD', 'AU', FALSE, '2022-09-08 00:00:00'),
    ('bid-15741422', 'id-95898841', 'Iris Anderson',   'Barclays',      '1034486969', '015803252', 'GBP', 'FR', FALSE, '2002-05-11 00:00:00'),
    ('bid-33423734', 'id-95898841', 'Leo Anderson',    'Chase',         '7027616681', '378641723', 'AUD', 'US', TRUE,  '2021-07-07 00:00:00'),
    ('bid-26141738', 'id-95927351', 'Leo Garcia',      'Citibank',      '9973045566', '741362696', 'AUD', 'FR', FALSE, '2017-10-03 00:00:00'),
    ('bid-98378936', 'id-97897752', 'Bob Thomas',      'Barclays',      '3161487805', '552260497', 'EUR', 'FR', TRUE,  '2008-02-24 00:00:00'),
    ('bid-64477441', 'id-34235738', 'Bob Williams',    'HSBC',          '2924781712', '479842632', 'CAD', 'DE', FALSE, '2023-06-25 00:00:00');

-- --------------------------------------------------------
-- Table: transactions
-- --------------------------------------------------------
CREATE TABLE "transactions" (
    "transaction_id" INTEGER PRIMARY KEY,
    "account_id" INTEGER,
    "reference_number" VARCHAR(30),
    "transaction_type" VARCHAR(30),
    "amount" DECIMAL(18,2),
    "currency" VARCHAR(3),
    "exchange_rate" DECIMAL(18,2),
    "balance_after" DECIMAL(18,2),
    "description" VARCHAR(255),
    "channel" VARCHAR(20),
    "status" VARCHAR(20),
    "created_at" TIMESTAMP,
    FOREIGN KEY ("account_id") REFERENCES "accounts"("account_id")
);

INSERT INTO "transactions" ("transaction_id", "account_id", "reference_number", "transaction_type", "amount", "currency", "exchange_rate", "balance_after", "description", "channel", "status", "created_at") VALUES
    (1219, 1351, 'TXN-ML95333099', 'WITHDRAWAL', 32123.36, 'AUD', 1.29, 157670.61, 'Utility bill payment', 'MOBILE', 'REVERSED',  '2007-09-12 00:00:00'),
    (7879, 9757, 'TXN-BP93539139', 'DEBIT',      49697.85, 'GBP', 2.91, 353351.95, 'ATM withdrawal',       'MOBILE', 'PENDING',   '2019-04-17 00:00:00'),
    (9532, 9757, 'TXN-GJ07927584', 'FEE',        49093.25, 'USD', 1.71, 142173.77, 'Wire transfer',        'ATM',    'PENDING',   '2012-10-28 00:00:00'),
    (4781, 9136, 'TXN-QP06907795', 'CREDIT',     22347.39, 'AUD', 0.99, 289866.39, 'Payroll deposit',      'MOBILE', 'COMPLETED', '2000-07-04 00:00:00'),
    (5744, 2012, 'TXN-RP44619131', 'INTEREST',   35324.40, 'EUR', 1.48, 171330.73, 'Monthly fee',          'ATM',    'COMPLETED', '2016-11-10 00:00:00'),
    (468,  2012, 'TXN-FQ34537449', 'INTEREST',    1505.86, 'AUD', 0.78, 451753.90, 'Utility bill payment', 'API',    'REVERSED',  '2010-10-13 00:00:00'),
    (2295, 1351, 'TXN-YP60988392', 'DEBIT',      35193.45, 'CAD', 3.16, 310720.45, 'ATM withdrawal',       'ONLINE', 'REVERSED',  '2005-08-10 00:00:00'),
    (664,  3153, 'TXN-ZV80657574', 'INTEREST',   35146.06, 'EUR', 0.59, 347199.18, 'ATM withdrawal',       'POS',    'COMPLETED', '2015-11-29 00:00:00'),
    (191,  8396, 'TXN-JL68997007', 'INTEREST',   35895.16, 'CAD', 2.22, 163066.43, 'Monthly fee',          'API',    'FAILED',    '2000-01-24 00:00:00'),
    (712,  8379, 'TXN-CT80704244', 'INTEREST',    1179.34, 'GBP', 3.07, 407963.91, 'Mortgage payment',     'API',    'COMPLETED', '2019-02-23 00:00:00'),
    (8402, 9757, 'TXN-CI83077273', 'WITHDRAWAL', 14142.26, 'AUD', 3.24, 124595.15, 'ATM withdrawal',       'API',    'COMPLETED', '2024-12-13 00:00:00'),
    (9828, 3153, 'TXN-NB16292337', 'DEBIT',      26867.03, 'EUR', 1.77,  70869.25, 'ATM withdrawal',       'API',    'REVERSED',  '2018-10-22 00:00:00'),
    (6646, 8245, 'TXN-QK67151201', 'DEBIT',      15898.20, 'AUD', 1.87,  33418.38, 'Interest payment',     'ATM',    'REVERSED',  '2014-07-30 00:00:00'),
    (4660, 1778, 'TXN-KR04135478', 'DEPOSIT',    14059.04, 'CAD', 2.26, 401832.28, 'ATM withdrawal',       'ATM',    'ON_HOLD',   '2001-09-10 00:00:00'),
    (9536, 8245, 'TXN-AH35309913', 'CREDIT',     24967.69, 'CAD', 2.05,  29940.95, 'Interest payment',     'ONLINE', 'PENDING',   '2020-06-23 00:00:00'),
    (8526, 3889, 'TXN-OU81793119', 'INTEREST',   44785.14, 'GBP', 2.43, 484211.72, 'Monthly fee',          'API',    'ON_HOLD',   '2025-09-07 00:00:00'),
    (4159, 2012, 'TXN-VM26632471', 'WITHDRAWAL', 42253.66, 'GBP', 1.86,  86466.15, 'Interest payment',     'MOBILE', 'FAILED',    '2017-08-08 00:00:00'),
    (8458, 7123, 'TXN-JR65961117', 'INTEREST',   34073.00, 'EUR', 1.88, 284777.45, 'Wire transfer',        'MOBILE', 'PENDING',   '2003-05-11 00:00:00'),
    (3367, 1273, 'TXN-OH06388372', 'FEE',         1752.02, 'USD', 2.42, 469769.21, 'Direct deposit',       'MOBILE', 'REVERSED',  '2021-07-08 00:00:00'),
    (367,  4886, 'TXN-HD46329470', 'CREDIT',     30848.82, 'AUD', 1.63, 261084.12, 'Online purchase',      'ATM',    'ON_HOLD',   '2001-11-25 00:00:00');

