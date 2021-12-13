import sqlalchemy as sql
import os

from sqlalchemy import Column, Date, Index, String, TIMESTAMP, Text, text
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, TINYINT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

BaseModel = declarative_base()
metadata = BaseModel.metadata

engine = sql.create_engine('mysql+pymysql://uusama:uusama@localhost:3306/dictionary?charset=utf8mb4')
session = sessionmaker(bind=engine)()


# 单词详情表
class Grammar(BaseModel):
    __tablename__ = 'grammar'

    id = Column(BIGINT(20), primary_key=True)
    content = Column(String(256), nullable=False, server_default=text("''"))
    level = Column(String(16), nullable=False, server_default=text("''"))
    category = Column(String(64), nullable=False, server_default=text("''"))
    type = Column(String(64), nullable=False, server_default=text("''"))
    link = Column(String(256), nullable=False, server_default=text("''"))
    explain = Column(String(512), nullable=False, server_default=text("''"))
    example = Column(String(1024), nullable=False, server_default=text("''"))
    postscript = Column(String(512), nullable=False, server_default=text("''"))
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class WordBook(BaseModel):
    __tablename__ = 'word_book'

    id = Column(BIGINT(20), primary_key=True)
    name = Column(String(128), nullable=False, server_default=text("''"))
    source = Column(String(64), nullable=False, server_default=text("''"))
    source_id = Column(BIGINT(20), primary_key=True)
    level = Column(String(16), nullable=False, server_default=text("''"))
    introduction = Column(String(256), nullable=False, server_default=text("''"))
    cover_image_url = Column(String(256), nullable=False, server_default=text("''"))
    from_lang = Column(String(16), nullable=False, server_default=text("''"))
    to_lang = Column(String(16), nullable=False, server_default=text("''"))
    word_count = Column(INTEGER(11), nullable=False, server_default=text("0"))
    learning_user_count = Column(INTEGER(11), nullable=False, server_default=text("0"))
    finish_user_count = Column(INTEGER(11), nullable=False, server_default=text("0"))
    word_queried = Column(TINYINT(1), nullable=False, server_default=text("0"))
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


def save_grammar(grammar: Grammar):
    if session.query(Grammar).filter(Grammar.id == grammar.id).first() is not None:
        print("The Grammar is exist. id:{} , content:{}".format(grammar.id, grammar.content))
        return

    session.merge(grammar)
    session.commit()


def ready_table():
    BaseModel.metadata.create_all(engine)
