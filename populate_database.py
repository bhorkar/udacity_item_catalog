from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from db_setup import *

class Populate_database:
    engine = create_engine('sqlite:///ItemCatalog.db')
    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    session = DBSession()

# Delete Categories if exisitng.
    session.query(Category).delete()
# Delete CatalogItems if exisitng.
    session.query(CatalogItem).delete()
# Delete Users if exisitng.
    session.query(User).delete()

# Create fake usersa

    users = [
        {
            'username': 'test',
            'email': 'test@gmail.com',
            'picture':'https://lh6.googleusercontent.com/-Nk2JadNaxDE/AAAAAAAAAAI/AAAAAAAAH-w/uQ18O3CGdfc/s96-c/photo.jpg'
        }
    ]


    def add_users(self):
	    for u in self.users:
		    self.session.add(User(
			username=u['username'],
			email=u['email'],
                        picture=u['picture']
		    ))
	    self.session.commit()
            user_genesis = self.session.query(User).filter_by(email='test@gmail.com').one()
	    cate1 = Category(name='Soccer', user_id = user_genesis.id)
	    self.session.add(cate1)
	    self.session.commit()
	    item1 = CatalogItem(name = "FIFA shirt women", description = "FIFA marks on the back and a big pink ball on the front",\
			     user_id = user_genesis.id, category = cate1)
	    self.session.add(item1)
	    self.session.commit()
	    item2 = CatalogItem(name = "FIFA shirt men", description = "FIFA marks on the back and a big black heart on the front", \
			     user_id = user_genesis.id, category = cate1)
	    self.session.add(item2)
	    self.session.commit()
	    cate2 = Category(name='Basketball', user_id = user_genesis.id)
	    self.session.add(cate2)
	    self.session.commit()
	    item1 = CatalogItem(name = "Nike Leather Basketballs", description = "Made out of fake leather", \
			     user_id = user_genesis.id, category = cate2)
	    self.session.add(item1)
	    self.session.commit()
	    item2 = CatalogItem(name = "Oversized Basketball vests", description = "rainball colors with different sizes", \
			     user_id = user_genesis.id, category = cate2)
	    self.session.add(item2)
	    self.session.commit()
	    cate3 = Category(name='Baseball', user_id = user_genesis.id)
	    self.session.add(cate3)
	    self.session.commit()
	    item1 = CatalogItem(name = "Yankee hats", description = "all hats are designer hats and the materials are extremely recyclable", \
			     user_id = user_genesis.id, category = cate3)
	    self.session.add(item1)
	    self.session.commit()
	    item2 = CatalogItem(name = "baseballs bats", description = "Different colors are available. You can also pre-order with your chosen color",\
			     user_id = user_genesis.id, category = cate3)
	    self.session.add(item2)
	    self.session.commit()
	    cate4 = Category(name='Snowboarding', user_id = user_genesis.id)
	    self.session.add(cate4)
	    self.session.commit()
	    item1 = CatalogItem(name = "Goggles", description = "Goggles are made out of lime stones, and they all are imported from Netherland", \
			     user_id = user_genesis.id, category = cate4)
	    self.session.add(item1)
	    self.session.commit()
		
	    item2 = CatalogItem(name = "Snowboards", description = "Different Length and different designs are available for all professional levels", \
			     user_id = user_genesis.id, category = cate4)
	    self.session.add(item2)
	    self.session.commit()
		
	    cate5 = Category(name='Swimming', user_id = user_genesis.id)
	    self.session.add(cate5)
	    self.session.commit()
	    item1 = CatalogItem(name = "Swimming suits", description = "Roxy brands and alike are available. \
				       They are made out of materials that are environmentally friendly", \
			     user_id = user_genesis.id, category = cate5)
	    self.session.add(item1)
	    self.session.commit()
		
	    item2 = CatalogItem(name = "Swimming Goggles", description = "They are all on sale. Different colors are available", 
			     user_id = user_genesis.id, category = cate5)
	    self.session.add(item2)
	    self.session.commit()
	    cate6 = Category(name='Hockey', user_id = user_genesis.id)
	    self.session.add(cate6)
	    self.session.commit()
	    cate7 = Category(name='Skating', user_id = user_genesis.id)
	    self.session.add(cate7)
	    self.session.commit()
	    cate8 = Category(name='Football', user_id = user_genesis.id)
	    self.session.add(cate8)
	    self.session.commit()
	    cate9 = Category(name='Rock Climbing', user_id = user_genesis.id)
	    self.session.add(cate9)
	    self.session.commit()
	    print("CatalogItemCatalog Database populated!")
	    print("Checking Catagories ...")
	    cates = self.session.query(Category).all()
	    for cate in cates:
		    print('{} has the following items'.format(cate.name))
		    items = self.session.query(CatalogItem).filter_by(category = cate).all()
		    for item in items:
                       print(item.name)




pop = Populate_database()
pop.add_users()
    
