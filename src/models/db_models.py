"""数据库模型定义"""
from sqlalchemy import Column, String, Float, Integer, Text, JSON, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database import Base


class City(Base):
    """城市表"""
    __tablename__ = "cities"
    
    city_id = Column(String(50), primary_key=True, comment="城市ID")
    city_name = Column(String(100), nullable=False, index=True, comment="城市名称")
    province = Column(String(100), comment="省份")
    country = Column(String(100), default="中国", comment="国家")
    description = Column(Text, comment="城市描述")
    tags = Column(JSON, default=list, comment="标签列表")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系
    attractions = relationship("Attraction", back_populates="city", cascade="all, delete-orphan")
    locations = relationship("Location", back_populates="city", cascade="all, delete-orphan")
    hotels = relationship("Hotel", back_populates="city", cascade="all, delete-orphan")
    restaurants = relationship("Restaurant", back_populates="city", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<City(city_id='{self.city_id}', name='{self.city_name}')>"


class Attraction(Base):
    """景点表"""
    __tablename__ = "attractions"
    
    attraction_id = Column(String(50), primary_key=True, comment="景点ID")
    name = Column(String(200), nullable=False, index=True, comment="景点名称")
    city_id = Column(String(50), ForeignKey("cities.city_id"), nullable=False, index=True, comment="城市ID")
    category = Column(String(50), nullable=False, comment="类别：scenic_spot/museum/park/beach/mountain/temple")
    description = Column(Text, comment="景点描述")
    address = Column(String(500), comment="地址")
    latitude = Column(Float, comment="纬度")
    longitude = Column(Float, comment="经度")
    opening_hours = Column(String(200), comment="开放时间")
    ticket_price = Column(Float, default=0, comment="门票价格")
    recommended_duration = Column(String(50), comment="建议游览时长（小时）")
    tags = Column(JSON, default=list, comment="标签列表")
    rating = Column(Float, comment="评分（0-5）")
    images = Column(JSON, default=list, comment="图片URL列表")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系
    city = relationship("City", back_populates="attractions")
    
    def __repr__(self):
        return f"<Attraction(attraction_id='{self.attraction_id}', name='{self.name}')>"


class Location(Base):
    """地点表（交通枢纽、商业区等）"""
    __tablename__ = "locations"
    
    location_id = Column(String(50), primary_key=True, comment="地点ID")
    name = Column(String(200), nullable=False, index=True, comment="地点名称")
    city_id = Column(String(50), ForeignKey("cities.city_id"), nullable=False, index=True, comment="城市ID")
    category = Column(String(50), nullable=False, comment="类别：airport/train_station/bus_station/metro/shopping/food")
    address = Column(String(500), comment="地址")
    latitude = Column(Float, comment="纬度")
    longitude = Column(Float, comment="经度")
    description = Column(Text, comment="描述")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系
    city = relationship("City", back_populates="locations")
    
    def __repr__(self):
        return f"<Location(location_id='{self.location_id}', name='{self.name}')>"


class Hotel(Base):
    """酒店表"""
    __tablename__ = "hotels"
    
    hotel_id = Column(String(50), primary_key=True, comment="酒店ID")
    name = Column(String(200), nullable=False, index=True, comment="酒店名称")
    city_id = Column(String(50), ForeignKey("cities.city_id"), nullable=False, index=True, comment="城市ID")
    address = Column(String(500), comment="地址")
    latitude = Column(Float, comment="纬度")
    longitude = Column(Float, comment="经度")
    star_rating = Column(Integer, comment="星级（1-5）")
    price_range = Column(String(50), comment="价格区间：budget/mid-range/luxury")
    min_price = Column(Float, comment="最低价格")
    max_price = Column(Float, comment="最高价格")
    amenities = Column(JSON, default=list, comment="设施列表")
    description = Column(Text, comment="描述")
    rating = Column(Float, comment="评分（0-5）")
    images = Column(JSON, default=list, comment="图片URL列表")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系
    city = relationship("City", back_populates="hotels")
    
    def __repr__(self):
        return f"<Hotel(hotel_id='{self.hotel_id}', name='{self.name}')>"


class Restaurant(Base):
    """餐厅表"""
    __tablename__ = "restaurants"
    
    restaurant_id = Column(String(50), primary_key=True, comment="餐厅ID")
    name = Column(String(200), nullable=False, index=True, comment="餐厅名称")
    city_id = Column(String(50), ForeignKey("cities.city_id"), nullable=False, index=True, comment="城市ID")
    cuisine_type = Column(String(100), comment="菜系类型")
    address = Column(String(500), comment="地址")
    latitude = Column(Float, comment="纬度")
    longitude = Column(Float, comment="经度")
    price_level = Column(String(50), comment="价格等级：$/$$/$$$/$$$$")
    avg_price = Column(Float, comment="人均消费")
    specialties = Column(JSON, default=list, comment="特色菜品")
    description = Column(Text, comment="描述")
    rating = Column(Float, comment="评分（0-5）")
    opening_hours = Column(String(200), comment="营业时间")
    images = Column(JSON, default=list, comment="图片URL列表")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系
    city = relationship("City", back_populates="restaurants")
    
    def __repr__(self):
        return f"<Restaurant(restaurant_id='{self.restaurant_id}', name='{self.name}')>"
