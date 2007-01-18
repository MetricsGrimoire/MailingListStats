
CREATE TABLE mailing_lists(
mailing_list_url varchar(400) primary key,
mailing_list_name varchar(60) unique,
project_name varchar(30),
last_analysis datetime) ENGINE=INNODB;


CREATE TABLE compressed_files(
url varchar(50) primary key,
status enum('new', 'visited', 'failed'),
last_analysis datetime,
mailing_list_url varchar(400),
foreign key (mailing_list_url) references mailing_lists(mailing_list_url) on delete cascade) ENGINE=INNODB;


CREATE TABLE messages(
message_id char(128) primary key,
author_from varchar(60),
author_alias varchar(40),
mailing_list varchar(40),
first_date datetime,
arrival_date datetime,
subject varchar(100),
message_body text,
mailing_list_url varchar(400),
is_response_of char(128),
mail_path text,
foreign key (mailing_list_url) references mailing_lists(mailing_list_url) on delete cascade,
foreign key (is_response_of) references messages(message_id) on delete cascade ) ENGINE=INNODB;


CREATE TABLE people(
email_address varchar(60) primary key,
alias varchar(60)) ENGINE=INNODB;


CREATE TABLE messages_people(
email_address char(60),
type_of_recipient enum('To','Cc','Bcc'),
message_id char(128),
foreign key (email_address) references people(email_address) on delete cascade ,
foreign key (message_id) references message(message_id) on delete cascade ) ENGINE=INNODB;


CREATE TABLE mailing_lists_people(
email_address varchar(60),
mailing_list_url varchar(400),
foreign key (email_address) references people(email_address) on delete cascade ,
foreign key (mailing_list_url) references mailing_lists(mailing_list_url) on delete cascade) ENGINE=INNODB;

