Obtained with PyDofus

Items.json is obtained by decompiling Items.d2o

i18n_fr.json is obtained by decompiling i18n_fr.d2i

Then, given an item GID, you have to find in Items.json the entry with 
```'id': <corresponding gid>``` ,
then you will have an entry "nameId": xxxx
And you can use this number to search for the name in i18n_fr.json

For the subcategories, it is the same thing with ItemTypes.json instead of Items.json