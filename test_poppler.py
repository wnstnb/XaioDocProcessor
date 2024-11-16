FORM_1120S_PAGE1_MAPPINGS = {
    # Header Information
    'tax_year_begin': {
        'label': 'For calendar year 2023 or tax year beginning',
        'type': 'date',
        'section': 'header'
    },
    'tax_year_end': {
        'label': 'ending',
        'type': 'date',
        'section': 'header'
    },
    # Company Information
    'company_name': {
        'label': 'Name',
        'type': 'text',
        'section': 'identification'
    },
    'company_address': {
        'label': 'Number, street, and room or suite no.',
        'type': 'text',
        'section': 'identification'
    },
    'company_city_state_zip': {
        'label': 'City or town, state or province, country, and ZIP or foreign postal code',
        'type': 'text',
        'section': 'identification'
    },
    # Key Information
    's_election_date': {
        'label': 'A S election effective date',
        'type': 'date',
        'section': 'identification'
    },
    'ein': {
        'label': 'D Employer identification number',
        'type': 'text',
        'section': 'identification'
    },
    'business_code': {
        'label': 'B Business activity code number',
        'type': 'text',
        'section': 'identification'
    },
    'date_incorporated': {
        'label': 'E Date incorporated',
        'type': 'date',
        'section': 'identification'
    },
    'total_assets': {
        'label': 'F Total assets',
        'type': 'currency',
        'section': 'identification'
    },
    # Income Items
    'gross_receipts': {
        'label': '1a Gross receipts or sales',
        'type': 'currency',
        'section': 'income'
    },
    'returns_allowances': {
        'label': '1b Less returns and allowances',
        'type': 'currency',
        'section': 'income'
    },
    'balance': {
        'label': '1c Balance',
        'type': 'currency',
        'section': 'income',
        'calculation': 'gross_receipts - returns_allowances'
    },
    'cost_of_goods_sold': {
        'label': '2 Cost of goods sold',
        'type': 'currency',
        'section': 'income'
    },
    'gross_profit': {
        'label': '3 Gross profit',
        'type': 'currency',
        'section': 'income',
        'calculation': 'balance - cost_of_goods_sold'
    },
    'net_gain_4797': {
        'label': '4 Net gain (loss) from Form 4797',
        'type': 'currency',
        'section': 'income'
    },
    'other_income': {
        'label': '5 Other income (loss)',
        'type': 'currency',
        'section': 'income'
    },
    'total_income': {
        'label': '6 Total income (loss)',
        'type': 'currency',
        'section': 'income',
        'calculation': 'sum(gross_profit, net_gain_4797, other_income)'
    },
    # Deduction Items
    'officer_compensation': {
        'label': '7 Compensation of officers',
        'type': 'currency',
        'section': 'deductions'
    },
    'salaries_wages': {
        'label': '8 Salaries and wages',
        'type': 'currency',
        'section': 'deductions'
    },
    'repairs_maintenance': {
        'label': '9 Repairs and maintenance',
        'type': 'currency',
        'section': 'deductions'
    },
    'bad_debts': {
        'label': '10 Bad debts',
        'type': 'currency',
        'section': 'deductions'
    },
    'rents': {
        'label': '11 Rents',
        'type': 'currency',
        'section': 'deductions'
    },
    'taxes_licenses': {
        'label': '12 Taxes and licenses',
        'type': 'currency',
        'section': 'deductions'
    },
    'interest': {
        'label': '13 Interest',
        'type': 'currency',
        'section': 'deductions'
    },
    'depreciation': {
        'label': '14 Depreciation',
        'type': 'currency',
        'section': 'deductions'
    },
    'depletion': {
        'label': '15 Depletion',
        'type': 'currency',
        'section': 'deductions'
    },
    'advertising': {
        'label': '16 Advertising',
        'type': 'currency',
        'section': 'deductions'
    },
    'pension_profit_sharing': {
        'label': '17 Pension, profit-sharing, etc., plans',
        'type': 'currency',
        'section': 'deductions'
    },
    'employee_benefits': {
        'label': '18 Employee benefit programs',
        'type': 'currency',
        'section': 'deductions'
    },
    'energy_efficient_deduction': {
        'label': '19 Energy efficient commercial buildings deduction',
        'type': 'currency',
        'section': 'deductions'
    },
    'other_deductions': {
        'label': '20 Other deductions',
        'type': 'currency',
        'section': 'deductions'
    },
    'total_deductions': {
        'label': '21 Total deductions',
        'type': 'currency',
        'section': 'deductions',
        'calculation': 'sum(lines_7_through_20)'
    },
    'ordinary_business_income': {
        'label': '22 Ordinary business income (loss)',
        'type': 'currency',
        'section': 'bottom_line',
        'calculation': 'total_income - total_deductions'
    }
}

# Helper function to get fields by section
def get_fields_by_section(section):
    return {k: v for k, v in FORM_1120S_PAGE1_MAPPINGS.items() if v['section'] == section}

# Helper function to get calculated fields
def get_calculated_fields():
    return {k: v for k, v in FORM_1120S_PAGE1_MAPPINGS.items() if 'calculation' in v}

# Example usage:
if __name__ == "__main__":
    # Print all income fields
    income_fields = get_fields_by_section('income')
    print("Income Fields:")
    for field, details in income_fields.items():
        print(f"{field}: {details['label']}")
    
    # Print all calculated fields
    calculated_fields = get_calculated_fields()
    print("\nCalculated Fields:")
    for field, details in calculated_fields.items():
        print(f"{field}: {details['calculation']}")
