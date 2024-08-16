"""
数据库ORM封装
"""
import re
import json
from datetime import datetime, date
from typing import Optional, Type, List

from sqlalchemy import Column, DateTime, String, Integer, Date, BigInteger, Boolean, text, Text, CLOB
from sqlalchemy.orm import attributes, Query
from contextlib import contextmanager
from sqlalchemy.orm import Session, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, DeclarativeMeta
from base.config import load_config
from base.log import logger


CONFIG = {
    # oracle+cx_oracle://your_username:your_password@your_host:your_port/service_name
    'SQLALCHEMY_DATABASE_URI': r'sqlite:///cache/info.db',
}
load_config(CONFIG)

engine = create_engine(
    CONFIG['SQLALCHEMY_DATABASE_URI'],
    # json_serializer=lambda obj: json.dumps(obj, ensure_ascii=False),  # oracle不支持
)

SessionLocal: sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
Base: DeclarativeMeta = declarative_base()
scoped_session = scoped_session(SessionLocal)


@contextmanager
def session_scope():
    """
    提供一个上下文管理器，用于管理session的生命周期。
    在with语句块内，你可以使用session进行数据库操作。
    当离开with语句块时，session会自动提交或回滚，并关闭。
    """
    session = scoped_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class BaseModel(Base):
    """
    基础模型
    """
    # 这是一个抽象基类，不会被直接映射到数据库表
    __abstract__ = True

    # id = Column(Integer, primary_key=True, comment="主键ID")
    create_time = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    def to_dict(self) -> dict:
        """
        将SQLAlchemy模型实例转换为字典
        :return:
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            # 如果值是SQLAlchemy关系对象（例如外键关联的对象），则递归调用model_to_dict
            if isinstance(value, attributes.InstrumentedAttribute):
                value = value.to_dict()
                # 处理SQLAlchemy的日期和时间对象，将它们转换为ISO格式的字符串
            elif isinstance(value, (datetime, date)):
                value = value.isoformat()
                # 处理其他可能的复杂类型，如列表、集合等
            # ...
            result[column.name] = value
        return result

    def to_json(self):
        """
        将SQLAlchemy模型实例转换为JSON字符串
        :return:
        """
        model_dict = self.to_dict()
        return json.dumps(model_dict)


class AmberProductDetail(BaseModel):
    """
    json示例，分不同tab项
    """
    __table_args__ = {
        'comment': '协会备案产品全要素信息'
    }
    __tablename__ = 'amber_product_detail'

    # 主要字段
    product_id = Column(BigInteger, nullable=False, primary_key=True, comment='产品ID')
    product_code = Column(String(64), nullable=False, unique=True, comment='产品编码')
    product_name = Column(String(255), nullable=False, comment='产品名称')
    product_short_name = Column(String(128), nullable=False, comment='产品简称')
    found_date = Column(DateTime, comment='成立日期')
    due_date = Column(DateTime, comment='到期日期')
    contract_operation_mode = Column(String(64), comment='合同信息-运作模式，seal：封闭运作，fixDate：定期开放，other：其他')
    contract_operation_mode_other = Column(String(64), comment='合同信息-运作模式为其他的值')

    income_assignment_count = Column(String(16), comment='合同信息-收益分配次数-类型，Y:每年收益分配，Z:每年收益分配不超过, other:其他')
    income_assignment_value = Column(String(256), comment='合同信息-收益分配次数-值')
    income_assignment_condition = Column(String(1024), comment='合同信息-收益分配条件')

    has_third_org = Column(String(4), comment='是否有投资顾问')
    # CLOB类型的所有字段必须放在后面，否则会报错 https://docs.oracle.com/en/error-help/db/ora-24816/?r=23ai
    third_org_counselor = Column(CLOB, comment='投资顾问信息，json字符串，其中是一个数组')
    tax_and_cost_bc = Column(CLOB, comment='业绩报酬，json字符串，其中是一个数组')
    source_json = Column(CLOB, comment='原始json字符串')


class BaseRepository(object):

    def __init__(self, model: Type[BaseModel]):
        self.model = model

    def get_session(self) -> Session:
        return session_manager.get_session()

    def get_by_id(self, id: int) -> Optional[BaseModel]:
        return self.get_session().query(self.model).get(id)

    def get_all(self) -> List[Type[BaseModel]]:
        return self.get_session().query(self.model).all()

    def transfer_db_data(self, data: dict):
        db_data = {}
        for key, value in data.items():
            # 处理cameCase驼峰命名字段以及全大写字段，转成小写字符加下划线分割单词
            if key.isupper():
                # 处理全大写字段，转为全小写，如 RMNDF -> rmndf
                key = key.lower()
            elif key.isalnum():
                # 处理cameCase驼峰命名字段，如 productShortName -> product_short_name
                key = re.sub(r'([a-z])([A-Z])', r'\1_\2', key).lower()
            if key in self.model.__table__.columns:
                db_data[key] = value
        return db_data

    def create_from_dict(self, data: dict) -> Type[BaseModel]:
        db_data = self.transfer_db_data(data)
        instance = self.model(**db_data)
        self.get_session().add(instance)
        self.do_commit()
        self.get_session().refresh(instance)
        self.do_commit()
        return instance

    def update_from_dict(self, data: dict) -> Type[BaseModel]:
        db_data = self.transfer_db_data(data)
        instance = self.get_session().query(self.model).get(db_data['id'])
        instance.update(db_data)
        self.do_commit()
        return instance

    def save_from_dict(self, data: dict, unique_key: str):
        # 根据unique_key查询，如果数据存在则更新，如果不存在则新建
        db_data = self.transfer_db_data(data)
        instance = self.get_session().query(self.model).filter_by(**{unique_key: db_data[unique_key]}).first()
        if instance:
            # 遍历字典并更新用户模型的属性
            for key, value in db_data.items():
                # 确保字典中的键是User模型的有效属性
                if hasattr(instance, key) and key != unique_key:  # 假设我们不直接改变主键
                    setattr(instance, key, value)
            self.do_commit()
        else:
            return self.create_from_dict(db_data)

    def delete(self, item_id: int):
        instance = self.get_session().query(self.model).get(item_id)
        if instance:
            self.get_session().delete(instance)
            self.do_commit()

    def do_commit(self):
        try:
            self.get_session().commit()
        except Exception:
            logger.error('commit db error and rollback.', stack_info=True, exception=True)
            self.get_session().rollback()


def create_tables():
    Base.metadata.create_all(bind=engine)


def reset_tables():
    # 删除指定表
    # AmberProductDetail.__table__.drop(engine)
    Base.metadata.drop_all(bind=engine)
    create_tables()


if __name__ == '__main__':
    # reset_tables()
    create_tables()
