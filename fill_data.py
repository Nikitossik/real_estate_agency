from api.generator.generator import Generator
import time
from app import app

#Initializing data with generator class

gen = Generator(app)
    
start_time = time.time() 
    
gen.gen_users(10000, True)
gen.gen_properties()
gen.gen_listing()
gen.gen_applications()
gen.initialize_sales()
gen.gen_sale_payments()
gen.initialize_rentals()
gen.terminate_contracts()
gen.terminate_contracts(listing_type="rental")
    
end_time = time.time() 
    
print(f"Database generation: {(end_time - start_time):.6f}s")
