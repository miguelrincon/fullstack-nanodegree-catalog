## Item Catalog

The item catalog is part of the the Fullstack Developer Nanodegree program. It is a catalog of items which allows people to view products sorted by category in a web application.

It allows users to register and create, edit or delete their own products using third-party authentication. The authentication is provided by Github Oauth API.

It aims to fulfill the rubric: https://review.udacity.com/#!/rubrics/5/view

### Run the project

#### Requirements

This project uses Python 3

Requires a few third-party Python libraries:
```
pip3 install httplib2
pip3 install flask
pip3 install sqlalchemy
```

#### Setup

1) Create a new Github app, you can do so here https://github.com/settings/apps

2) Obtiain Github app client id and client secret

3) Create a config file and use the json format below:
```
$ touch config/github_secrets.json
{
    "web": {
        "app_id": "APP_ID",
        "app_secret": "APP_SECRET"
    }
}
```
4) Create and populate the database

```
$ rm -f data/catalog.db   # Clean old data if needed
$ python3 ./scripts/database_setup.py 
$ python3 ./scripts/database_populate.py 
```

### Run the project

```
python3 catalog.py
```

Visit http://localhost:5001

### A brief API documentation

The project provides a few GET endpoints to allow other applications to consume the item data, all ids are numeric:

1) Get data of a category
```
GET http://localhost:5001/category/2.json

{
  "created_at": "Wed, 05 Dec 2018 08:05:17 GMT", 
  "id": 2, 
  "name": "Food", 
  "updated_at": "Wed, 05 Dec 2018 08:05:17 GMT", 
  "user_id": null
}
```

2) Get data of an item
```
GET http://localhost:5001/item/5.json

{
  "category_id": 2, 
  "created_at": "Wed, 05 Dec 2018 08:05:17 GMT", 
  "description": "The most chocolatastic cookie. Only one left.", 
  "id": 5, 
  "name": "A Cookie", 
  "updated_at": "Wed, 05 Dec 2018 08:05:17 GMT", 
  "user_id": 1
}
```

2) Get items of a category
```
GET http://localhost:5001/category/2/items.json

[
  {
    "category_id": 2, 
    "created_at": "Wed, 05 Dec 2018 08:05:17 GMT", 
    "description": "The most chocolatastic cookie. Only one left.", 
    "id": 5, 
    "name": "A Cookie", 
    "updated_at": "Wed, 05 Dec 2018 08:05:17 GMT", 
    "user_id": 1
  }, 
  {
    "category_id": 2, 
    "created_at": "Wed, 05 Dec 2018 08:05:17 GMT", 
    "description": "Also known as french fries.", 
    "id": 6, 
    "name": "Some chips", 
    "updated_at": "Wed, 05 Dec 2018 08:05:17 GMT", 
    "user_id": null
  }
]
```
