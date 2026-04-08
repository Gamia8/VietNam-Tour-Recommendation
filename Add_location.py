import pandas as pd
import dateparser
import re
from datetime import datetime
from Latitude_longitude import get_manual_address

def normalize_date(date_str):        # chuẩn hóa ngày
    try:
        parsed_date = dateparser.parse(date_str, settings={'RELATIVE_BASE': datetime(2025, 6, 21)})
        return parsed_date.strftime('%Y-%m-%d') if parsed_date else "No date"
    except:
        return "No date"

def clean_content(text):              # Làm sạch nội dung
    if not isinstance(text, str) or len(text.strip()) < 5:
        return "No valid comment"
    text = re.sub(r'[^\w\s]', '', text) 
    text = re.sub(r'\s+', ' ', text).strip().lower()  
    return text if text else "No valid comment"

def add_location_data(input_file, output_file):
    df = pd.read_csv(input_file)
    df['date'] = df['date'].apply(normalize_date)
    df['address_info'] = df['place_name'].apply(get_manual_address)
    df['address'] = df['address_info'].apply(lambda x: x['address'])
    df['latitude'] = df['address_info'].apply(lambda x: x['latitude'])
    df['longitude'] = df['address_info'].apply(lambda x: x['longitude'])

    df = df.drop(columns=['address_info'])
    df['content'] = df['content'].apply(clean_content)
    
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Processed data has been saved to '{output_file}'")
    return df