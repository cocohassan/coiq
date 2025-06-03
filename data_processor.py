import pandas as pd
import numpy as np
from typing import Tuple
import country_converter as coco

class DataProcessor:
    # Fund level mapping for rocket type classification
    FUND_LEVEL_MAPPING = {
        "Pre Seed": "W",
        "Preseed": "W",
        "No Funding": "W",
        "No Investment": "W",
        "Seed": "X",
        "Seed & Bridge": "X",
        "Bridge": "X",
        "Series A": "Y",
        "Series B": "Z"
    }
    
    # Dictionary mapping countries to their approximate center coordinates
    COUNTRY_COORDS = {
        'Palestine': {'lat': 31.9522, 'lon': 35.2332},
        'SaudiArabia': {'lat': 23.8859, 'lon': 45.0792},
        'Indonesia': {'lat': -0.7893, 'lon': 113.9213},
        'Malaysia': {'lat': 4.2105, 'lon': 101.9758},
        'Canada': {'lat': 56.1304, 'lon': -106.3468},
        'UnitedKingdom': {'lat': 55.3781, 'lon': -3.4360},
        'UnitedStates': {'lat': 37.0902, 'lon': -95.7129},
        'Nigeria': {'lat': 9.0820, 'lon': 8.6753},
        'India': {'lat': 20.5937, 'lon': 78.9629},
        'UnitedArabEmirates': {'lat': 23.4241, 'lon': 53.8478},
        'Singapore': {'lat': 1.3521, 'lon': 103.8198},
        'Namibia': {'lat': -22.9576, 'lon': 18.4904},
        'Pakistan': {'lat': 30.3753, 'lon': 69.3451},
        'Uzbekistan': {'lat': 41.3775, 'lon': 64.5853},
        'Zambia': {'lat': -13.1339, 'lon': 27.8493},
        'France': {'lat': 46.2276, 'lon': 2.2137},
        'Malawi': {'lat': -13.2543, 'lon': 34.3015},
        'Austria': {'lat': 47.5162, 'lon': 14.5501},
        'SouthAfrica': {'lat': -30.5595, 'lon': 22.9375},
        'Turkey': {'lat': 38.9637, 'lon': 35.2433},
        'Bangladesh': {'lat': 23.6850, 'lon': 90.3563},
        'Switzerland': {'lat': 46.8182, 'lon': 8.2275},
        'Qatar': {'lat': 25.3548, 'lon': 51.1839},
        'Egypt': {'lat': 26.8206, 'lon': 30.8025},
        'Morocco': {'lat': 31.7917, 'lon': -7.0926},
        'Brunei': {'lat': 4.5353, 'lon': 114.7277},
        'Germany': {'lat': 51.1657, 'lon': 10.4515},
        'Australia': {'lat': -25.2744, 'lon': 133.7751},
        'Tunisia': {'lat': 33.8869, 'lon': 9.5375},
        'Angola': {'lat': -11.2027, 'lon': 17.8739}
    }

    @staticmethod
    def normalize_fund_level(input_value):
        """Normalize the fund level string to ensure consistency."""
        return str(input_value).strip().title()

    @staticmethod
    def classify_stage(fund_level):
        """Classify the stage (rocket type) based on the fund level."""
        normalized = DataProcessor.normalize_fund_level(fund_level)
        return DataProcessor.FUND_LEVEL_MAPPING.get(normalized, "Unknown")

    @staticmethod
    def process_csv(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
        """
        Process the CSV data and classify startups according to the required format
        """
        # Use the uploaded data - no fallback to demo data
        processed_df = df.copy()
        
        # Return empty stats if no data is provided
        if df.empty:
            return df, {
                'total_startups': 0,
                'rocket_type_distribution': {},
                'percentages': {},
                'country_distribution': {}
            }
        
        # Filter for only "For Profit" rockets based on the "Type" column
        if 'Type' in processed_df.columns:
            processed_df = processed_df[processed_df['Type'].str.strip().str.lower() == "for profit"].copy()
        
        # Calculate rocket type based on Fund level if Fund level column exists
        if 'Fund level' in processed_df.columns:
            processed_df['rocket_type'] = processed_df['Fund level'].apply(DataProcessor.classify_stage)
        
        # Ensure we have the right column names for compatibility
        if 'rocket_type' in processed_df.columns and 'Final Label' not in processed_df.columns:
            processed_df = processed_df.rename(columns={'rocket_type': 'Final Label'})
        
        # Add latitude and longitude based on country if not already present
        if 'Country' in processed_df.columns:
            if 'latitude' not in processed_df.columns or 'longitude' not in processed_df.columns:
                processed_df['latitude'] = processed_df['Country'].map(lambda x: DataProcessor.COUNTRY_COORDS.get(x, {'lat': 0})['lat'])
                processed_df['longitude'] = processed_df['Country'].map(lambda x: DataProcessor.COUNTRY_COORDS.get(x, {'lon': 0})['lon'])
        
        # Calculate statistics
        stats = {
            'total_startups': len(processed_df),
            'rocket_type_distribution': processed_df['Final Label'].value_counts().to_dict() if 'Final Label' in processed_df.columns else {},
            'percentages': (processed_df['Final Label'].value_counts(normalize=True) * 100).round(2).to_dict() if 'Final Label' in processed_df.columns else {},
            'country_distribution': processed_df.groupby('Country')['Final Label'].value_counts().unstack().fillna(0).to_dict() if 'Country' in processed_df.columns and 'Final Label' in processed_df.columns else {}
        }
        
        return processed_df, stats