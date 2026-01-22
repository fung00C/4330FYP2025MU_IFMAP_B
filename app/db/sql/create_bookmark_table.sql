CREATE TABLE if not EXISTS bookmark (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL,
    stock_symbol TEXT NOT NULL,

    FOREIGN KEY (email) REFERENCES user (email) ON DELETE CASCADE,
    UNIQUE (email, stock_symbol) -- Ensures a user cannot bookmark the same stock multiple times
);
