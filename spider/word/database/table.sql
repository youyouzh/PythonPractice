create database dictionary;

use dictionary;

drop table if exists grammar;

create table grammar
(
	id bigint auto_increment,
	content varchar(256) not null comment '语法内容',
	level varchar(16) not null comment '语法等级',
	category varchar(64) not null comment '分类',
	type varchar(64) comment '语法类型',
	link varchar(256) not null comment '语法接续',
	`explain` varchar(512) not null comment '详解',
	example varchar(1024) not null comment '例句',
	postscript varchar(512) comment '补充说明',
	created_at timestamp default current_timestamp not null,
	updated_at timestamp default current_timestamp not null,
	constraint table_name_pk primary key (id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 comment '日语语法';

create table word (
    id bigint auto_increment,
    name varchar(128) not null comment '单词',
    `language` varchar(16) not null comment '语言： jp, zh, eng',
    kana varchar(64) not null comment '',
    roma varchar(64) not null comment '',
    accent varchar(64) not null comment '音标',
    level varchar(8) comment '等级',
    pos varchar(64) not null comment '词性'
)