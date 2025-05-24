import requests
import pandas as pd
import time

API_KEY = ''
HEADERS = {
    'Authorization': f'Bearer {API_KEY}',
}
LOCATIONS = ['Cheney, WA', 'Spokane, WA', 'Spokane Valley, WA', 'Coeur d\'Alene, ID']

def search_businesses(location):
    url = 'https://api.yelp.com/v3/businesses/search'
    params = {
        'term': 'restaurants',
        'location': location,
        'limit': 50,
        'sort_by': 'rating'
    }
    res = requests.get(url, headers=HEADERS, params=params)
    return res.json().get('businesses', [])

def get_business_details(business_id):
    url = f'https://api.yelp.com/v3/businesses/{business_id}'
    res = requests.get(url, headers=HEADERS)
    return res.json()

def has_cheesecake(text):
    return 'cheesecake' in text.lower()

def infer_dessert(categories, name):
    text = ' '.join(cat['title'] for cat in categories) + ' ' + name
    return any(word in text.lower() for word in ['dessert', 'sweet', 'bakery', 'cake', 'ice cream'])

all_data = []

for location in LOCATIONS:
    print(f"Searching in {location}...")
    businesses = search_businesses(location)
    
    for b in businesses:
        details = get_business_details(b['id'])
        time.sleep(0.2)

        name = b.get('name')
        types = ', '.join([c['title'] for c in b.get('categories', [])])
        address = ', '.join(b.get('location', {}).get('display_address', []))
        price = b.get('price', 'N/A')
        url = b.get('url', '')
        dessert = infer_dessert(b.get('categories', []), name)
        cheesecake = has_cheesecake(details.get('description', '') + name + types)
        
        hours = 'N/A'
        hours_data = details.get('hours', [])
        if hours_data:
            for h in hours_data[0].get('open', []):
                if h['day'] == 5:  #Saturday
                    closing_raw = h.get('end', '')
                    if closing_raw:
                        closing_formatted = f"{closing_raw[:2]}:{closing_raw[2:]}"
                        hours = closing_formatted
                        break  #stop after Saturday entry

        all_data.append({
            'Name': name,
            'Type': types,
            'Location': address,
            'Hours': hours,
            'Price': price,
            'Dessert?': 'Yes' if dessert else 'No',
            'CHEESECAKE?': 'Yes' if cheesecake else 'No',
            'Menu': url
        })

#Save to Excel
df = pd.DataFrame(all_data)
df.to_excel('graduation_dinner_options.xlsx', index=False)

print("Saved to graduation_dinner_options.xlsx")
