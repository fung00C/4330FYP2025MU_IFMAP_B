CREATE TABLE if not EXISTS notification_setting (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    frequency TEXT NOT NULL CHECK (frequency IN ('daily', 'weekly', 'monthly')) default 'daily',
    day_of_week TEXT CHECK (day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday')),
    date_of_month INTEGER CHECK (date_of_month >= 1 AND date_of_month <= 31),
    time_of_day TEXT NOT NULL default '08:00',

    FOREIGN KEY (email) REFERENCES user (email) ON DELETE CASCADE,
    UNIQUE (email) -- Ensures a user cannot have duplicate notification settings
);