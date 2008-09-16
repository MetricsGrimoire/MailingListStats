
CREATE TABLE people (
  people_ID INTEGER UNSIGNED NOT NULL,
  email_address VARCHAR(255) NOT NULL,
  name VARCHAR(255) NULL,
  username VARCHAR(255) NULL,
  domain_name VARCHAR(255) NULL,
  top_level_domain VARCHAR(255) NULL,
  PRIMARY KEY(people_ID),
  UNIQUE INDEX email_address_index(email_address)
)
TYPE=InnoDB;


CREATE TABLE mailing_lists (
  mailing_list_url VARCHAR(255) NOT NULL,
  mailing_list_name VARCHAR(255) NULL DEFAULT 'NULL',
  project_name VARCHAR(255) NULL DEFAULT 'NULL',
  last_analysis DATETIME NULL,
  PRIMARY KEY(mailing_list_url)
)
TYPE=InnoDB;

CREATE TABLE tool_info (
  project VARCHAR(255) NOT NULL,
  tool VARCHAR(255) NULL,
  tool_version VARCHAR(255) NULL,
  datasource VARCHAR(255) NULL,
  datasource_info TEXT NULL,
  creation_date DATETIME NULL,
  last_modification DATETIME NULL,
  PRIMARY KEY(project)
)
TYPE=InnoDB;

CREATE TABLE messages (
  message_ID VARCHAR(255) NOT NULL,
  mailing_list_url VARCHAR(255) NOT NULL,
  mailing_list VARCHAR(255) NULL,
  first_date DATETIME NULL,
  first_date_tz INTEGER(11) NULL,
  arrival_date DATETIME NULL,
  arrival_date_tz INTEGER(11) NULL,
  subject VARCHAR(255) NULL,
  message_body TEXT NULL,
  is_response_of VARCHAR(255) NULL,
  mail_path TEXT NULL,
  PRIMARY KEY(message_ID),
  INDEX response(is_response_of),
  FOREIGN KEY(mailing_list_url)
    REFERENCES mailing_lists(mailing_list_url)
      ON DELETE CASCADE
      ON UPDATE CASCADE,
  FOREIGN KEY(is_response_of)
    REFERENCES messages(message_ID)
      ON DELETE CASCADE
      ON UPDATE CASCADE,
)
TYPE=InnoDB;

CREATE TABLE compressed_files (
  url VARCHAR(255) NOT NULL,
  mailing_list_url VARCHAR(255) NOT NULL,
  status ENUM('new','visited','failed') NULL,
  last_analysis DATETIME NULL,
  PRIMARY KEY(url),
  FOREIGN KEY(mailing_list_url)
    REFERENCES mailing_lists(mailing_list_url)
)
TYPE=InnoDB;


CREATE TABLE mailing_lists_people (
  people_ID INTEGER UNSIGNED NOT NULL,
  mailing_list_url VARCHAR(255) NOT NULL,
  PRIMARY KEY(people_ID, mailing_list_url),
  FOREIGN KEY(mailing_list_url)
    REFERENCES mailing_lists(mailing_list_url)
      ON DELETE CASCADE
      ON UPDATE CASCADE,
  FOREIGN KEY(people_ID)
    REFERENCES people(people_ID)
      ON DELETE CASCADE
      ON UPDATE CASCADE
)
TYPE=InnoDB;


CREATE TABLE messages_people (
  type_of_recipient ENUM('From','To','Cc') NOT NULL DEFAULT 'From',
  message_id VARCHAR(255) NOT NULL,
  people_ID INTEGER UNSIGNED NOT NULL,
  PRIMARY KEY(type_of_recipient, message_id, people_ID),
  INDEX m_id(message_id),
  FOREIGN KEY(message_ID)
    REFERENCES messages(message_id)
      ON DELETE CASCADE
      ON UPDATE CASCADE,
  FOREIGN KEY(people_ID)
    REFERENCES people(people_ID)
      ON DELETE CASCADE
      ON UPDATE CASCADE
)
TYPE=InnoDB;


