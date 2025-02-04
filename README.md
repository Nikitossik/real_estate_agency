
# Real Estate AGency API

A pet-project for a univercity task, that simulates a real estate agency database filled with real-world data from Kaggle Dataset using Generator class. Project also contains RESTful API made with Flask, SQLAlchemy with SwaggerUI documentation.

## Main technologies used

- Development stack: Python Flask, Flask-SQLAlchemy, flask-swagger-ui, Faker, pandas
- Database: PostgreSQL
- Dataset: [Kaggle Apartment Prices in Poland](https://www.kaggle.com/datasets/krzysztofjamroz/apartment-prices-in-poland)

## Run Locally

Clone the project

```bash
  git clone https://github.com/Nikitossik/real_estate_agency
```

Go to the project directory

```bash
  cd real_estate_agency
```

Install dependencies

```bash
  pip install -r requirements.txt
```
### Note: 
You have to create a local database and run DDL script from `database/schema.sql` to set up all tables and functions used in the database 

Populate the database with data

```bash
  py fill_data.py
```

Run Flask app

```bash
  flask run
```

Open Swagger Docs of the API at `http://127.0.0.1:5000/docs/`
