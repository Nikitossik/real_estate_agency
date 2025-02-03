from faker import Faker
import glob
import pandas as pd
import random
import os
import pytz
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import math
from api.models import *
from sqlalchemy import text

fake = Faker('pl_PL')

class Generator:
    
    # a filepath for processed property data
    _processed_filepath = "./api/generator/data/properties/processed/property.csv"
    
    def __init__(self, app):
        self.app = app
        self.db = db
        
    # HELPER FUNCTIONS
    
    def _clear_table(self, model):
        with self.app.app_context():
            self.db.session.execute(text(f'TRUNCATE TABLE public.{model.__tablename__} CASCADE;'))
            self.db.session.commit()
    
    def gen_users(self, num, overwrite = False):
        
        #generates users with fake data
        
        if overwrite:
            self._clear_table(User)
            
        users_data = [
            {
                "user_name": fake.first_name(),
                "user_surname": fake.last_name(),
                "user_email": fake.unique.email(),
                "user_phone": fake.phone_number(),
                "bank_account": ''.join(fake.random_choices(elements=('0123456789'), length=16))
            } for _ in range(num)
        ]
        
        with self.app.app_context():
            self.db.session.bulk_insert_mappings(User, users_data)
            self.db.session.commit()
            print(f'Added {len(users_data)} users')
            
    def gen_properties(self, users_sample = 50):
        
        # gets property data from file and adds owners
        
        self._clear_table(Property)
        
        with self.app.app_context():
        
            property_df = pd.read_csv(self._processed_filepath)
            owner_ids_df = pd.read_sql(f"SELECT user_id from public.user TABLESAMPLE SYSTEM({users_sample})", self.db.engine)
            owner_ids = owner_ids_df['user_id'].tolist()
            
            single_property_ids = owner_ids[:int( len(owner_ids) * 0.7 )]
            multi_property_ids = owner_ids[int( len(owner_ids) * 0.3 ):]
            
            property_df["owner_id"] = pd.concat([
                pd.Series(single_property_ids),
                pd.Series(multi_property_ids).repeat(random.randint(2, 10))
            ]).sample(len(property_df), replace=True, random_state=42).values
        
            property_data = property_df.to_dict(orient="records")
            self.db.session.bulk_insert_mappings(Property, property_data)
            self.db.session.commit()
            print(f'Added {len(property_data)} properties')
        

    def gen_listing(self, property_sample = 90):
        
        # generates ads for most properties(90 percent)
    
        self._clear_table(Listing)
        
        with self.app.app_context():
        
            property_db = pd.read_sql(f"SELECT * FROM property TABLESAMPLE SYSTEM({property_sample})", self.db.engine)
            property_df = pd.read_csv(self._processed_filepath).sample(n=len(property_db))
            
            property_db['listing_price'] = property_df['price'].values
            property_db['listing_type'] = property_df['listing_type'].values
            
            property_db.rename(columns={
                'property_id': 'id_property',
                'owner_id': 'id_user'    
            }, inplace=True)
            
            start_date = datetime(2024, 4, 1)
            
            for idx, row in property_db.iterrows():
                random_datetime = fake.date_time_between_dates(datetime_start=start_date, datetime_end="now", 
                    tzinfo=pytz.timezone('Europe/Warsaw'))
                
                property_db.loc[idx, 'created_at'] = random_datetime
                property_db.loc[idx, 'listing_description'] = fake.paragraph(nb_sentences=5)
                
            listing_data = property_db.to_dict(orient="records")
            self.db.session.bulk_insert_mappings(Listing, listing_data)
            self.db.session.commit()
            print(f'Added {len(listing_data)} listings')
        
    def gen_applications(self, listing_sample = 90, clients_sample = 80):
        
        self._clear_table(Application)
        
        with self.app.app_context():
        
            listing_df = pd.read_sql(f"SELECT listing_id, created_at FROM listing TABLESAMPLE SYSTEM({listing_sample})", self.db.engine)
            clients_df = pd.read_sql(f"""SELECT * FROM public.user u TABLESAMPLE SYSTEM({clients_sample}) WHERE u.user_id NOT IN (
                    SELECT DISTINCT p.owner_id
                    FROM public.property p);""", 
            self.db.engine)
            
            applications_data = []
            
            for client_idx, client in clients_df.iterrows():
                listing_choice = listing_df.sample(n=random.randint(1,5))
                
                for list_idx, listing in listing_choice.iterrows():
        
                    applications_data.append({
                        "id_user": client['user_id'],
                        "id_listing": listing['listing_id'],
                        "created_at":fake.date_time_between_dates(datetime_start=listing['created_at'], datetime_end='now', 
                            tzinfo=pytz.timezone('Europe/Warsaw')),
                        "application_message":fake.paragraph(nb_sentences=5),
                        "is_submitted":False
                    })
                    
            self.db.session.bulk_insert_mappings(Application, applications_data)
            self.db.session.commit()
            print(f'Added {len(applications_data)} applications')
        
    def initialize_sales(self, application_sample = 50):
        
        # calls postgres func to add a sale contract based on randomly picked application 
        
        self._clear_table(Sale)
        
        with self.app.app_context():
        
            applications_df = pd.read_sql(f"""
                SELECT application_id, id_listing, a.created_at
                FROM application a TABLESAMPLE SYSTEM({application_sample})
                JOIN listing l ON a.id_listing = l.listing_id
                WHERE l.listing_status = 'active' AND l.listing_type = 'sale' AND a.is_submitted = FALSE;
            """, self.db.engine)
        
            applications_df = applications_df.groupby('id_listing').apply(lambda x: x.sample(1)).reset_index(drop=True)        

            for idx, row in applications_df.iterrows():
                row['created_at'] = row['created_at'] + timedelta(days=random.randint(1, 3), 
                        seconds= random.randint(0, 86400))
        
            for idx, row in applications_df.iterrows():
                self.db.session.execute(text(f"SELECT initialize_sale({row['application_id']}, '{row['created_at']}');"))
            self.db.session.commit()
            print(f'Added {len(applications_df)} sales')
            
        
    def gen_sale_payments(self, sales_sample = 70):
        
        # adds randomly multiple payments for sale contracts
        
        self._clear_table(Payment)
        
        with self.app.app_context():
        
            sales_df = pd.read_sql(f'SELECT * FROM sale TABLESAMPLE SYSTEM({sales_sample})', self.db.engine)
            
            payments_data = []
            
            for idx, row in sales_df.iterrows():
                
                # divide a price in multiple payments and send random number of them
                
                num_payments = random.randint(1, 6)
                actual_payments = random.randint(1, num_payments)
                payment_amount = math.ceil(row['sale_price'] / num_payments)
                
                start_date = row['created_at']
                end_date = start_date + timedelta(days=random.randint(actual_payments, actual_payments  * 4))
                
                payment_timestamps = sorted([
                    fake.date_time_between_dates(datetime_start=start_date, datetime_end=end_date)
                    for _ in range(actual_payments)
                ])
                
                for sent_at in payment_timestamps:
                    payments_data.append({
                        "payment_amount": payment_amount, 
                        "sent_at": sent_at, 
                        "id_sale": row['sale_id'], 
                        "id_sender": row['id_buyer']}
                    )
                    
            # when inserting values to payment table, postgres fires a trigger function
            # to check if the sum of payments is enough to make the buyer a new owner 
                
            self.db.session.bulk_insert_mappings(Payment, payments_data)
            self.db.session.commit()
            print(f'Added {len(payments_data)} payments')
        
    def initialize_rentals(self, rentals_sample = 50):
        
        # calls postges func to add rental contracts
        
        self._clear_table(Rental)
        
        with self.app.app_context():
        
            applications_df = pd.read_sql(f"""
                SELECT application_id, id_listing, a.created_at
                FROM application a TABLESAMPLE SYSTEM({rentals_sample})
                JOIN listing l ON a.id_listing = l.listing_id
                WHERE l.listing_status = 'active' AND l.listing_type = 'rent' AND a.is_submitted = FALSE;
            """, self.db.engine)
            
            applications_df = applications_df.groupby('id_listing').apply(lambda x: x.sample(1)).reset_index(drop=True)  
            
            for idx, row in applications_df.iterrows():
                
                start_date = row['created_at'].date() + timedelta(days=random.randint(1, 7))
                end_date = start_date + relativedelta(months=random.choice([3,6,12,24]))
                applications_df.loc[idx, 'start_date'] = start_date
                applications_df.loc[idx, 'end_date'] = end_date
                
            for idx, row in applications_df.iterrows():
                self.db.session.execute(text(f"SELECT initialize_rental({row['application_id']}, '{row['start_date']}', '{row['end_date']}');"))
            self.db.session.commit()
            print(f'Added {len(applications_df)} rentals')
        
    def terminate_contracts(self, listing_type = 'sale', contracts_sample = 50):
        
        # terminates either sale or rental table rows based on listing_type
        
        sales_query = f"""
            SELECT s.sale_id as contract_id, s.created_at
                FROM sale s TABLESAMPLE SYSTEM({contracts_sample})
                LEFT JOIN payment p ON s.sale_id = p.id_sale
                WHERE p.id_sale IS NULL and s.sale_status = 'active';
        """
        rentals_query = f"""
            SELECT r.rental_id as contract_id, r.start_date, r.end_date
                FROM rental r TABLESAMPLE SYSTEM({contracts_sample})
                WHERE r.rental_status = 'active';
        """
        termination_reasons = ['owner_request', 'client_request', 'force_majeure', 'payment_issue',
                    'legal_dispute', 'personal_reasons']
        
        with self.app.app_context():
        
            contracts_df = pd.read_sql(sales_query if listing_type == 'sale' else rentals_query, self.db.engine)
            
            for contract_idx, contract in contracts_df.iterrows():
                contracts_df.loc[contract_idx, 'termination_reason'] = random.choice(termination_reasons)
                contracts_df.loc[contract_idx, 'termination_details'] = fake.paragraph(nb_sentences=3)
                
                if listing_type == 'sale':
                    random_datetime = contract['created_at'] + timedelta(days=random.randint(3, 8))
                else:
                    random_datetime = fake.date_time_between_dates(datetime_start=contract['start_date'], 
                        datetime_end=contract['end_date'])
                
                contracts_df.loc[contract_idx, 'terminated_at'] = random_datetime
                
            # call a postgres function based on listing_type
            
            for idx, row in contracts_df.iterrows():
                self.db.session.execute(text(f"SELECT {'terminate_' + listing_type}('{row['contract_id']}', '{row['termination_reason']}', '{row['termination_details']}', '{row['terminated_at']}');"))
            self.db.session.commit()
            print(f'Terminated {len(contracts_df)} {listing_type}s')

    def process_property(self):
        
        # filelist for reading 
        
        file_list = glob.glob("./data/properties/original/*.csv")

        # removing output file if exists

        if os.path.exists(self._processed_filepath):
            os.remove(self._processed_filepath)

        dataframes = []
        
        # appending all the data to a dataframe
        
        for file in file_list:
            file_name = os.path.basename(file)
            
            df = pd.read_csv(file)
            
            # determine listing_type for future needs based on filename
            
            df['listing_type'] = 'rent' if 'rent' in file_name.lower() else 'sale'
            
            dataframes.append(df)

        combined_df = pd.concat(dataframes, ignore_index=True)

        # filter most common null values
    
        filtered_df = combined_df[
            combined_df["floor"].notna() &         
            combined_df["floorCount"].notna() & 
            combined_df['buildYear'].notna() & 
            combined_df['type'].notna()
        ]
        
        # replacing duplicating uuids with unique ones
        
        duplicates = filtered_df[filtered_df.duplicated(subset='id', keep=False)]
        duplicates['id'] = duplicates.apply(lambda _: ''.join(fake.uuid4().split('-')), axis=1)
        filtered_df.update(duplicates)
        
        # renaming columns as in db table
        
        filtered_df.rename(columns={
            'id': 'property_id',
            'squareMeters': 'square_meters',
            'floor': 'floor_value',
            'floorCount': 'floor_count',
            'type': 'building_type',
            'buildYear': 'build_year',
            'centreDistance': 'centre_distance'
        }, inplace=True)
        
        columns = ['property_id', 'city', 'latitude', 'longitude', 'rooms', 'square_meters', 'floor_value', 'floor_count', 
            'building_type', 'build_year', 'centre_distance', 'listing_type', 'price']
        
        # writing a df with specified columns to a target file 
        
        filtered_df.to_csv("./data/properties/processed/property.csv", columns=columns, index=False)
        