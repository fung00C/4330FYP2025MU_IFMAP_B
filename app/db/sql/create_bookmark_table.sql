CREATE TABLE if not EXISTS bookmark (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    stock_symbol TEXT NOT NULL,
    notify BOOLEAN DEFAULT FALSE NOT NULL,

    FOREIGN KEY (email) REFERENCES user (email) ON DELETE CASCADE,
    UNIQUE (email, stock_symbol, notify) -- Ensures a user cannot bookmark the same stock multiple times
);
