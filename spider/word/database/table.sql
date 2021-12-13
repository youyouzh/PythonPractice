create database dictionary;

use dictionary;

drop table if exists grammar;

create table grammar
(
	id bigint auto_increment primary key,
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
	index `content` (`content`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 comment '日语语法';

create table word_book
(
	id bigint auto_increment primary key,
	source varchar(64) not null comment '词书来源，如沪江，芥末日语考级',
	source_id bigint not null comment '词汇来源id',
	name varchar(128) not null comment '词书名称',
	level varchar(16) not null comment '词书等级，如N1，N2',
	introduction varchar(256) not null comment '语法接续',
	cover_image_url varchar(256) not null comment '',
	from_lang varchar(16) not null comment '词书原语言',
	to_lang varchar(16) not null comment '词书目标语言',
	word_count int not null comment '单词数量',
	learning_user_count int not null comment '学习人数，基于source数据',
	finish_user_count int not null comment '学完人数，基于source数据',
	word_queried tinyint(1) not null comment '是否词汇下载完成',
	created_at timestamp default current_timestamp not null,
	updated_at timestamp default current_timestamp not null,
	index `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 comment '词书';

create table word_book_to_word
(
    id bigint auto_increment primary key,
    word_id bigint not null comment '单词id',
    word_book_id bigint not null comment '词书id',
	created_at timestamp default current_timestamp not null,
	updated_at timestamp default current_timestamp not null,
	index `index_word_book_id_word_id` (`word_book_id`, `word_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 comment '词书对单词映射';

create table word (
    id bigint auto_increment primary key,
    source varchar(64) not null comment '词汇来源，如沪江，芥末日语考级',
    source_id bigint not null comment '词汇来源id',
    name varchar(128) not null comment '单词',
	from_lang varchar(16) not null comment '词书原语言： jp, zh, en',
	to_lang varchar(16) not null comment '词书目标语言： jp, zh, en',
    kana varchar(64) not null comment '',
    roma varchar(64) not null comment '',
    accent varchar(64) not null comment '音标',
    level varchar(8) comment '等级',
    pos varchar(64) not null comment '词性',
	created_at timestamp default current_timestamp not null,
	updated_at timestamp default current_timestamp not null,
	index `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 comment '单词';