import pandas as pd
import requests, time, os, json
from config import SHEETS_DIR, SHOPER_LIMIT

class ShoperAPIClient:

    def __init__(self, site_url, login, password):

        self.site_url = site_url
        self.login = login
        self.password = password
        self.session = requests.Session()
        self.token = None

    def connect(self):
        """Authenticate with the API"""
        response = self.session.post(
            f'{self.site_url}/webapi/rest/auth',
            auth=(self.login, self.password)
        )

        if response.status_code == 200:
            self.token = response.json().get('access_token')
            self.session.headers.update({'Authorization': f'Bearer {self.token}'})
            print("Shoper Authentication successful.")
        else:
            raise Exception(f"Authentication failed: {response.status_code}, {response.text}")

    def _handle_request(self, method, url, **kwargs):
        """Handle API requests with automatic retry on 429 errors."""
        while True:
            response = self.session.request(method, url, **kwargs)

            if response.status_code == 429:  # Too Many Requests
                retry_after = int(response.headers.get('Retry-After', 1))
                print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
            else:
                return response

    def get_all_products(self):
        products = []
        page = 1
        url = f'{self.site_url}/webapi/rest/products'

        print("Downloading all products.")
        while True: 
            params = {'limit': SHOPER_LIMIT, 'page': page}
            response = self._handle_request('GET', url, params=params)
            data = response.json()
            number_of_pages = data['pages']

            if response.status_code != 200:
                raise Exception(f"Failed to fetch data: {response.status_code}, {response.text}")

            page_data = response.json().get('list', [])

            if not page_data:  # If no data is returned
                break

            # FOR TESTING
            if page == 3:
                break

            print(f'Page: {page}/{number_of_pages}')
            products.extend(page_data)
            page += 1

        df = pd.DataFrame(products)
        df.to_excel(os.path.join(SHEETS_DIR, 'shoper_all_products.xlsx'), index=False)
        return df
    
    def get_a_single_product(self, product_id):
        url = f'{self.site_url}/webapi/rest/products/{product_id}'

        response = self._handle_request('GET', url)
        product = response.json()

        return product
    
    def get_a_single_product_by_code(self, product_code):
        url = f'{self.site_url}/webapi/rest/products'

        product_filter = {
            "filters": json.dumps({"stock.code": product_code})
        }

        try:
            response = self._handle_request('GET', url, params=product_filter)
            product_list = response.json().get('list', [])
            
            if not product_list:
                print(f'Product {product_code} doesn\'t exist')
                return None
            
            product = product_list[0]

            return product
        
        except Exception as e:
            print(f'Error fetching product {product_code}: {str(e)}')
            return None

    def get_all_products_and_select_special_offers(self):
        """Fetches all special offers and returns filtered DataFrame."""
        all_products = self.get_all_products()

        df = pd.DataFrame(all_products)
        
        df['product_name'] = df['translations'].apply(lambda x: x.get('pl_PL', {}).get('name', ''))
        df['price'] = df['stock'].apply(lambda x: x.get('price', '') if isinstance(x, dict) else '')
        df['date_from'] = df['special_offer'].apply(
            lambda x: pd.to_datetime(x.get('date_from', '')).strftime('%d-%m-%Y') 
            if isinstance(x, dict) and x.get('date_from') 
            else '')
        
        df['date_to'] = df['special_offer'].apply(
            lambda x: pd.to_datetime(x.get('date_to', '')).strftime('%d-%m-%Y') 
            if isinstance(x, dict) and x.get('date_to') 
            else '')

        # Filter rows where promo_price is not None
        df = df[df['promo_price'].notna()]
        

        # Select only needed columns
        columns_to_keep = [
            'code',
            'product_name',
            'price',
            'promo_price',
            'date_from',
            'date_to'
        ]
            
        df = df[columns_to_keep]
        
        # Save to Excel
        df.to_excel(os.path.join(SHEETS_DIR, 'shoper_all_special_offers.xlsx'), index=False)
        return df
    
    def create_a_special_offer(self, df):
        pass