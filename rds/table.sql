CREATE TABLE IF NOT EXISTS iot_event (
    id serial PRIMARY KEY,
    device_id TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    received_at TIMESTAMP NOT NULL
);
