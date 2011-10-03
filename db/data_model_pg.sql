-- PostgresQL schema

-- Create tables --
CREATE TABLE mailing_lists (
    mailing_list_url VARCHAR(255) NOT NULL,
    mailing_list_name VARCHAR(255),
    project_name VARCHAR(255),
    last_analysis TIMESTAMP,
    PRIMARY KEY(mailing_list_url)
    );

CREATE TABLE compressed_files (
    url VARCHAR(255) NOT NULL,
    mailing_list_url VARCHAR(255) NOT NULL,
    status VARCHAR(25) CHECK (status IN ('new', 'visited', 'failed')),
    last_analysis TIMESTAMP,
    PRIMARY KEY(url)
    );

CREATE TABLE people (
    email_address VARCHAR(255) NOT NULL, 
    name VARCHAR(255),
    username VARCHAR(255),
    domain_name VARCHAR(255),
    top_level_domain VARCHAR(255),
    PRIMARY KEY(email_address)
    );

CREATE TABLE messages (
    message_ID VARCHAR(255) NOT NULL,
    mailing_list_url VARCHAR(255) NOT NULL,
    mailing_list VARCHAR(255),
    first_date TIMESTAMP,
    first_date_tz NUMERIC(11),
    arrival_date TIMESTAMP,
    arrival_date_tz NUMERIC(11),
    subject VARCHAR(255),
    message_body TEXT,
    is_response_of VARCHAR(255),
    mail_path TEXT,
    PRIMARY KEY(message_ID)
    );
CREATE INDEX response ON messages (is_response_of);

CREATE TABLE messages_people (
    type_of_recipient VARCHAR(25) NOT NULL DEFAULT 'From'
        CHECK (type_of_recipient IN ('From', 'To', 'Cc')),
    message_id VARCHAR(255) NOT NULL,
    email_address VARCHAR(255) NOT NULL,
    PRIMARY KEY(type_of_recipient, message_id, email_address)
    );
CREATE INDEX m_id ON messages_people (message_id);

CREATE TABLE mailing_lists_people (
    email_address VARCHAR(255) NOT NULL,
    mailing_list_url VARCHAR(255) NOT NULL,
    PRIMARY KEY(email_address, mailing_list_url)
    )
