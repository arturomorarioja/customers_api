DROP TABLE IF EXISTS customer;

CREATE TABLE customer (
    nCustomerID INTEGER PRIMARY KEY AUTOINCREMENT,
    cFirstName TEXT NOT NULL,
    cLastName TEXT NOT NULL,
    cPhoneNo TEXT,
    cAddress TEXT NOT NULL,
    dOnboarding TEXT NOT NULL
);

INSERT INTO customer
    (cFirstName, cLastName, cPhoneNo, cAddress, dOnboarding)
VALUES
    ('Hjalte P.', 'Lorenzen', '20641910', 'Ulriksholmvej 42, 3730 Nexø', '20220621'),
    ('William S.', 'Poulsen', '81829903', 'Kamperhoug 52, 8245 Risskov Ø', '20170806'),
    ('Silke D.', 'Pedersen', '71174233', 'Muusgården 15, 5856 Ryslinge', '20200106'),
    ('Christian S.', 'Svendsen', '23358203', 'Mikkelenborgvej 7, 1367 København K', '20211002'),
    ('Emma T.', 'Berg', '', 'Bakkelunden 78, 5700 Svendborg', '20191210'),
    ('Stine N.', 'Nilsson', '23140595', 'Vestergade 1, 1787 København V', '20220501')