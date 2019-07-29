# coding: utf-8
from sqlalchemy import Column, Date, Index, String, TIMESTAMP, Text, text
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, TINYINT
from sqlalchemy.ext.declarative import declarative_base

BaseModel = declarative_base()
metadata = BaseModel.metadata


class Illustration(BaseModel):
    __tablename__ = 'illustration'

    id = Column(BIGINT(20), primary_key=True)
    user_id = Column(BIGINT(20), nullable=False, index=True)
    title = Column(String(255), nullable=False, server_default=text("''"))
    type = Column(String(50), nullable=False, server_default=text("''"))
    caption = Column(Text)
    restrict = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    create_date = Column(String(40), nullable=False, server_default=text("''"))
    page_count = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    width = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    height = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    sanity_level = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    x_restrict = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    total_view = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    total_bookmarks = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    is_bookmarked = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    visible = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    is_muted = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    total_comments = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    tools = Column(String(100), nullable=False, server_default=text("''"))
    image_url_square_medium = Column(String(255))
    image_url_medium = Column(String(255))
    image_url_large = Column(String(255))
    image_url_origin = Column(String(255))
    image_url_meta_origin = Column(String(255))
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class IllustrationTag(BaseModel):
    __tablename__ = 'illustration_tag'
    __table_args__ = (
        Index('uk_illust_id_tag_name', 'illust_id', 'name', unique=True),
    )

    id = Column(BIGINT(20), primary_key=True)
    user_id = Column(BIGINT(20), nullable=False, index=True)
    illust_id = Column(BIGINT(20), nullable=False, index=True)
    name = Column(String(50), nullable=False, server_default=text("''"))
    translated_name = Column(String(50), nullable=False, server_default=text("''"))
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class PixivUser(BaseModel):
    __tablename__ = 'pixiv_user'

    id = Column(BIGINT(20), primary_key=True)
    name = Column(String(50), nullable=False, server_default=text("''"))
    account = Column(String(50), nullable=False, unique=True, server_default=text("''"))
    comment = Column(String(255), nullable=False, server_default=text("''"))
    is_followed = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    webpage = Column(Text)
    gender = Column(String(20))
    birth = Column(Date)
    region = Column(String(20))
    address_id = Column(INTEGER(11))
    country_code = Column(String(20))
    job = Column(String(100))
    job_id = Column(INTEGER(11))
    total_follow_users = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    total_mypixiv_users = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    total_illusts = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    total_manga = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    total_novels = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    total_illust_bookmarks_public = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    total_illust_series = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    total_novel_series = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    background_image_url = Column(String(255))
    twitter_account = Column(String(255), nullable=False, server_default=text("''"))
    twitter_url = Column(String(255))
    pawoo_url = Column(String(255))
    is_premium = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    is_using_custom_profile_image = Column(TINYINT(1), server_default=text("'0'"))
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
