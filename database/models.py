from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    item_gid = Column(Integer, index=True)
    item_name = Column(String)
    sub_category_id = Column(Integer, ForeignKey('subcategories.id'))# casque/ dragodinde/ familier/ ...
    sub_category = relationship("SubCategory", back_populates="items")
    prices = relationship("PriceEntry", back_populates="item")

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    dofus_id = Column(Integer)
    name = Column(String, index=True)

class SubCategory(Base):
    __tablename__ = 'subcategories'
    id = Column(Integer, primary_key=True)
    dofus_id = Column(Integer)
    name = Column(String, index=True)
    items = relationship("Item", back_populates="sub_category")
    # category = Column(Integer, ForeignKey('categories.id'))

class PriceEntry(Base):
    __tablename__ = 'price_entries'

    id = Column(Integer, primary_key=True)
    price = Column(Integer)
    quantity = Column(Integer)
    item_id = Column(Integer, ForeignKey('items.id'))
    item = relationship("Item", back_populates="prices")
    created_ts = Column(DateTime)



export_class = {
    "PriceEntry": PriceEntry,
    "Item": Item,
}

if __name__ == "__main__":
    engine = create_engine('sqlite:///db.sqlite')
    Base.metadata.create_all(bind=engine)
