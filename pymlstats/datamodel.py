# Copyright (C) 2007 Libresoft Research Group
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors : Israel Herraiz <herraiz@gsyc.escet.urjc.es>

"""
This module contains the SQL code to create the schema of the database.

@authors:      Israel Herraiz
@organization: Libresoft Research Group, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      libresoft-tools-devel@lists.morfeo-project.org
"""

data_model_query_list = ["CREATE TABLE mailing_lists ( mailing_list_url VARCHAR(255) NOT NULL, mailing_list_name VARCHAR(255) NULL DEFAULT 'NULL', project_name VARCHAR(255) NULL DEFAULT 'NULL', last_analysis DATETIME NULL, PRIMARY KEY(mailing_list_url))ENGINE=InnoDB;",\
"CREATE TABLE compressed_files (url varchar(255) NOT NULL, mailing_list_url varchar(255) not null, status enum('new','visited','failed') null,  last_analysis datetime null,  primary key(url),  foreign key(mailing_list_url)   references mailing_lists(mailing_list_url))ENGINE=INNODB;",\
"CREATE TABLE people ( people_ID INTEGER UNSIGNED NOT NULL, email_address VARCHAR(255) NOT NULL, name VARCHAR(255) NULL, username VARCHAR(255) NULL,  domain_name VARCHAR(255) NULL, top_level_domain VARCHAR(255) NULL, PRIMARY KEY(people_ID), UNIQUE INDEX email_address_index(email_address))ENGINE=InnoDB;",\
"CREATE TABLE messages ( message_ID VARCHAR(255) NOT NULL,  mailing_list_url VARCHAR(255) NOT NULL,  mailing_list VARCHAR(255) NULL,  first_date DATETIME NULL,  first_date_tz INTEGER(11) NULL,  arrival_date DATETIME NULL,  arrival_date_tz INTEGER(11) NULL,  subject VARCHAR(255) NULL,  message_body TEXT NULL,  is_response_of VARCHAR(255) NULL,  mail_path TEXT NULL,  PRIMARY KEY(message_ID),  INDEX response(is_response_of), FOREIGN KEY(mailing_list_url)    REFERENCES mailing_lists(mailing_list_url)      ON DELETE CASCADE ON UPDATE CASCADE)ENGINE=InnoDB;",\
"CREATE TABLE messages_people ( type_of_recipient ENUM('From','To','Cc') NOT NULL DEFAULT 'From', message_id VARCHAR(255) NOT NULL, people_ID INTEGER UNSIGNED NOT NULL, PRIMARY KEY(type_of_recipient, message_id, people_ID), INDEX m_id(message_id), FOREIGN KEY(message_ID) REFERENCES messages(message_id)  ON DELETE CASCADE   ON UPDATE CASCADE, FOREIGN KEY(people_ID)   REFERENCES people(people_ID)  ON DELETE CASCADE  ON UPDATE CASCADE)ENGINE=InnoDB;",\
"CREATE TABLE mailing_lists_people ( people_ID INTEGER UNSIGNED NOT NULL, mailing_list_url VARCHAR(255) NOT NULL, PRIMARY KEY(people_ID, mailing_list_url),  FOREIGN KEY(mailing_list_url)    REFERENCES mailing_lists(mailing_list_url)   ON DELETE CASCADE   ON UPDATE CASCADE, FOREIGN KEY(people_ID)  REFERENCES people(people_ID)   ON DELETE CASCADE   ON UPDATE CASCADE)ENGINE=InnoDB;"]






