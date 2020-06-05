import json, os

from database.models import *
from database.utils import get_session

def add_names():
    with open(os.path.join("dofus_data", "i18n_fr.json")) as f:
        names = json.load(f).get("texts")
    session = get_session()

    items_without_name = session.query(Item).filter(Item.item_name==None).all()
    missing_ids = set([item.item_gid for item in items_without_name])

    # Todo: y'a moyen de reecrire cette merde bien plus proprement
    if items_without_name:
        with open(os.path.join("dofus_data", "Items.json")) as f:
            items = json.load(f)
        items_dict = {}
        for item in items:
            if item.get('id') in missing_ids:
                items_dict[item['id']] = names.get(str(item.get("nameId")))
        for item in items_without_name:
            item.item_name = items_dict[item.item_gid]

    categories_without_name = session.query(SubCategory).filter(SubCategory.name == None).all()
    missing_ids = set([category.dofus_id for category in categories_without_name])

    if categories_without_name:
        with open(os.path.join("dofus_data", "ItemTypes.json")) as f:
            categories = json.load(f)
        categories_dict = {}
        for category in categories:
            if category.get('id') in missing_ids:
                categories_dict[category['id']] = names.get(str(category.get("nameId")))
        for category in categories_without_name:
            category.name = categories_dict[category.dofus_id]

    session.commit()
    return

if __name__ == "__main__":
    add_names()