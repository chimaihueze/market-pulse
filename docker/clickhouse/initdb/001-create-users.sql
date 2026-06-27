CREATE DATABASE IF NOT EXISTS market_pulse;

CREATE USER IF NOT EXISTS market_pulse
IDENTIFIED WITH plaintext_password BY 'market_pulse_password';

GRANT ALL ON market_pulse.* TO market_pulse;
