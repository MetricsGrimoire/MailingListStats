-- MySQL schema

-- Create tables --
CREATE TABLE mailing_lists (
    mailing_list_url VARCHAR(255) CHARACTER SET utf8 NOT NULL,
    mailing_list_name VARCHAR(255) CHARACTER SET utf8 NULL DEFAULT 'NULL',
    project_name VARCHAR(255) CHARACTER SET utf8 NULL DEFAULT 'NULL',
    last_analysis DATETIME NULL,
    PRIMARY KEY(mailing_list_url))
ENGINE=InnoDB;

CREATE TABLE compressed_files (
    url varchar(255) CHARACTER SET utf8 NOT NULL,
    mailing_list_url varchar(255) CHARACTER SET utf8 not null,
    status enum('new','visited','failed') null,
    last_analysis datetime null,
    primary key(url),
    foreign key(mailing_list_url)
        references mailing_lists(mailing_list_url))
ENGINE=INNODB;

CREATE TABLE people (
    email_address VARCHAR(255) CHARACTER SET utf8 NOT NULL,
    name VARCHAR(255) CHARACTER SET utf8 NULL,
    username VARCHAR(255) CHARACTER SET utf8 NULL,
    domain_name VARCHAR(255) CHARACTER SET utf8 NULL,
    top_level_domain VARCHAR(255) CHARACTER SET utf8 NULL,
    PRIMARY KEY(email_address))
ENGINE=InnoDB;

CREATE TABLE messages (
    message_ID VARCHAR(255) CHARACTER SET utf8 NOT NULL,
    mailing_list_url VARCHAR(255) CHARACTER SET utf8 NOT NULL,
    mailing_list VARCHAR(255) CHARACTER SET utf8 NULL,
    first_date DATETIME NULL,
    first_date_tz INTEGER(11) NULL,
    arrival_date DATETIME NULL,
    arrival_date_tz INTEGER(11) NULL,
    subject VARCHAR(255) CHARACTER SET utf8 NULL,
    message_body MEDIUMTEXT CHARACTER SET utf8 NULL,
    is_response_of VARCHAR(255) CHARACTER SET utf8 NULL,
    mail_path TEXT CHARACTER SET utf8 NULL,
    PRIMARY KEY(message_ID),
    INDEX response(is_response_of),
    FOREIGN KEY(mailing_list_url)
        REFERENCES mailing_lists(mailing_list_url)
        ON DELETE CASCADE
        ON UPDATE CASCADE)
ENGINE=InnoDB;

CREATE TABLE messages_people (
    type_of_recipient ENUM('From','To','Cc') NOT NULL DEFAULT 'From',
    message_id VARCHAR(255) CHARACTER SET utf8 NOT NULL,
    email_address VARCHAR(255) CHARACTER SET utf8 NOT NULL,
    PRIMARY KEY(type_of_recipient, message_id, email_address),
    INDEX m_id(message_id),
    FOREIGN KEY(message_ID) REFERENCES messages(message_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY(email_address) REFERENCES people(email_address)
        ON DELETE CASCADE
        ON UPDATE CASCADE)
ENGINE=InnoDB;

CREATE TABLE mailing_lists_people (
    email_address VARCHAR(255) CHARACTER SET utf8 NOT NULL,
    mailing_list_url VARCHAR(255) CHARACTER SET utf8 NOT NULL,
    PRIMARY KEY(email_address, mailing_list_url),
    FOREIGN KEY(mailing_list_url)
        REFERENCES mailing_lists(mailing_list_url)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY(email_address)
        REFERENCES people(email_address)
        ON DELETE CASCADE
        ON UPDATE CASCADE)
ENGINE=InnoDB;
