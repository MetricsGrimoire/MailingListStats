CREATE TABLE mailing_lists(
mailing_list_url varchar(255) primary key,
mailing_list_name varchar(255) default null,
project_name varchar(255) default null,
last_analysis datetime) ENGINE=INNODB;


CREATE TABLE compressed_files(
url varchar(255) primary key,
status enum('new', 'visited', 'failed'),
last_analysis datetime,
mailing_list_url varchar(255),
index ml_url_a (mailing_list_url),
foreign key (mailing_list_url) references mailing_lists(mailing_list_url) on delete cascade) ENGINE=INNODB;


CREATE TABLE people(
email_address varchar(255) primary key,
name varchar(255),
username varchar(255),
domain_name varchar(255),
top_level_domain varchar(255)) ENGINE=INNODB;


CREATE TABLE messages(
message_id varchar(255) primary key,
author_email_address varchar(255),
mailing_list varchar(255),
first_date datetime,
first_date_tz int,
arrival_date datetime,
arrival_date_tz int,
subject varchar(255),
message_body text,
mailing_list_url varchar(255),
is_response_of varchar(255),
mail_path text,
index ml_url_c (mailing_list_url),
index response (is_response_of),
index email_c (author_email_address),
foreign key (mailing_list_url) references mailing_lists(mailing_list_url) on delete cascade,
foreign key (is_response_of) references messages(message_id) on delete cascade,
foreign key (author_email_address) references people(email_address) on delete cascade
) ENGINE=INNODB;


CREATE TABLE messages_people(
email_address varchar(255),
type_of_recipient enum('From','To','Cc'),
message_id varchar(255),
primary key(email_address,type_of_recipient,message_id),
index email_a (email_address),
index m_id (message_id),
foreign key (email_address) references people(email_address) on delete cascade,
foreign key (message_id) references messages(message_id) on delete cascade ) ENGINE=INNODB;


CREATE TABLE mailing_lists_people(
email_address varchar(255),
mailing_list_url varchar(255),
primary key (email_address, mailing_list_url),
index email_b (email_address),
index ml_url_b (mailing_list_url),
foreign key (email_address) references people(email_address) on delete cascade ,
foreign key (mailing_list_url) references mailing_lists(mailing_list_url) on delete cascade) ENGINE=INNODB;
