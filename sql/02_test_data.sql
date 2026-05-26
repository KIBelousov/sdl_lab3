INSERT INTO customers(full_name, email, phone)
VALUES
('Иван Иванов', 'ivan@test.com', '+79990000001'),
('Анна Смирнова', 'anna@test.com', '+79990000002');

INSERT INTO pet_categories(name)
VALUES
('Собаки'),
('Кошки'),
('Птицы');

INSERT INTO products(category_id, name, price, stock)
VALUES
(1, 'Корм Royal Canin для собак', 3500, 15),
(1, 'Поводок для собак', 1200, 30),
(2, 'Наполнитель для кошачьего туалета', 900, 25),
(2, 'Игрушка для кошек', 700, 18),
(3, 'Клетка для попугая', 5500, 5);

INSERT INTO orders(customer_id)
VALUES
(1),
(2);

INSERT INTO order_items(order_id, product_id, quantity, price)
VALUES
(1, 1, 2, 3500),
(1, 2, 1, 1200),
(2, 3, 3, 900);
