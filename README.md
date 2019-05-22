# Project:Item-Catalog
We are building a sports catalog

## Key Functionality
  - Google Authentication
  - Easy to add, update, create, delete information.
  - Easily accessible data with JSON Endpoints


### Prerequisites
  - Python 2.7
  -requirements.txt

### How to Run
- Clone this repository.
- Open your vagrant machine and change directory into this folder
- Run the python code catalog.py using the following command
` python3 catalog.py`
- Open your browser and go to this url http://localhost:8000

## JSON endpoints
#### Returns JSON of all Categories
`/bookstore/JSON/`
#### Returns JSON of all books in specific category
`/bookstore/<int:c_id>/JSON/`
#### Returns JSON of a given book
`/bookstore/<int:c_id>/vbook/<int:b_id>/JSON/`

https://github.com/br3ndonland/udacity-fsnd-flask-catalog/blob/master/info/flask-catalog-methods.md#google

