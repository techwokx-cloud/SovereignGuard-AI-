# config/frameworks.py

FRAMEWORKS = {
    'AfCFTA': {
        'name': 'African Continental Free Trade Area',
        'description': 'Agreement establishing the African Continental Free Trade Area',
        'effective_date': '2021-01-01',
        'countries': ['South Africa', 'Nigeria', 'Kenya', 'Tanzania', 'Ghana', 'Egypt'],
        'rules': {
            'rules_of_origin': True,
            'tariff_reduction': True,
            'sanctions_compliance': True
        }
    },
    'WTO': {
        'name': 'World Trade Organization',
        'description': 'WTO Agreement on Trade Facilitation',
        'effective_date': '1995-01-01',
        'countries': ['All WTO Members'],
        'rules': {
            'most_favored_nation': True,
            'national_treatment': True,
            'rules_of_origin': True,
            'tariff_binding': True
        }
    },
    'EU-UK': {
        'name': 'EU-UK Trade and Cooperation Agreement',
        'description': 'Agreement between the European Union and the United Kingdom',
        'effective_date': '2021-01-01',
        'countries': ['UK', 'France', 'Germany', 'Italy', 'Spain'],
        'rules': {
            'rules_of_origin': True,
            'tariff_classification': True,
            'sanctions_compliance': True
        }
    },
    'USMCA': {
        'name': 'United States-Mexico-Canada Agreement',
        'description': 'Agreement between the US, Mexico, and Canada',
        'effective_date': '2020-07-01',
        'countries': ['USA', 'Canada', 'Mexico'],
        'rules': {
            'rules_of_origin': True,
            'tariff_classification': True,
            'sanctions_compliance': True,
            'north_american_content': True
        }
    }
}

FRAMEWORK_RULES = {
    'AfCFTA': {
        'rules_of_origin': 'Goods must originate from African Union member states',
        'tariff_reduction': '90% of tariff lines to be reduced over 5-10 years',
        'sanctions_compliance': 'Must comply with UN and AU sanctions'
    },
    'WTO': {
        'most_favored_nation': 'Equal treatment for all WTO members',
        'national_treatment': 'Equal treatment for domestic and foreign goods',
        'rules_of_origin': 'Non-preferential rules of origin',
        'tariff_binding': 'Tariffs bound at specific rates'
    },
    'EU-UK': {
        'rules_of_origin': 'Products must originate from EU or UK',
        'tariff_classification': 'Proper classification under HS system',
        'sanctions_compliance': 'Compliance with EU sanctions'
    },
    'USMCA': {
        'rules_of_origin': 'Products must originate from North America',
        'tariff_classification': 'Proper classification under HS system',
        'sanctions_compliance': 'Compliance with US sanctions',
        'north_american_content': 'Minimum 75% North American content'
    }
}