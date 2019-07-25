#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlalchemy as sql

engine = sql.create_engine('mysql+pymysql://uusama:uusama@localhost:3306/pixiv?charset=utf8')
EntityBase = sql.ext.declarative.declarative_base()
session = sql.orm.sessionmaker(bind=engine)()


class IllustrationTag(EntityBase):
    __tablename__ = 'illustration_tag'
    id = sql.Column(sql.BigInteger, primary_key=True)
    user_id = sql.Column(sql.BigInteger)
    illust_id = sql.Column(sql.BigInteger)
    name = sql.Column(sql.String)
    translated_name = sql.Column(sql.String)
    created_at = sql.Column(sql.TIMESTAMP)
    updated_at = sql.Column(sql.TIMESTAMP)


records = [IllustrationTag(user_id=1, illust_id=1, name='test', translated_name='测试')]
session.add_all(records)
session.commit()
session.close()
