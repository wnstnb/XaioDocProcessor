from pydantic import BaseModel, Field
from typing import Type
from google import genai
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
# Create a client
api_key = os.getenv("GOOGLE_GENAI_API_KEY")
client = genai.Client(api_key=api_key)
 
# Define the model you are going to use
model_id =  "gemini-2.0-flash" # or "gemini-2.0-flash-lite-preview-02-05"  , "gemini-2.0-pro-exp-02-05"

# General extractor for 1120S, 1120, 1065
class BalanceSheet(BaseModel):
    tax_year: str = Field(description="The tax year of this form.")
    beginning_cash: str = Field(description="Find 'Cash' in Assets section and return the value for (b). If no value is found, return an empty string.")
    ending_cash: str = Field(description="Find 'Cash' in Assets section and return the value for (d). If no value is found, return an empty string.")
    beginning_accounts_receivable: str = Field(description="Find 'Less allowance for bad debts' in Assets section and return the value for (b). If no value is found, return an empty string.")
    ending_accounts_receivable: str = Field(description="Find 'Less allowance for bad debts' in Assets section and return the value for (d). If no value is found, return an empty string.")
    beginning_inventories: str = Field(description="Find 'Inventories' in Assets section and return the value for (b). If no value is found, return an empty string.")
    ending_inventories: str = Field(description="Find 'Inventories' in Assets section and return the value for (d). If no value is found, return an empty string.")
    beginning_total_assets: str = Field(description="Find 'Total Assets' in Assets section and return the value for (b). If no value is found, return an empty string.")
    ending_total_assets: str = Field(description="Find 'Total Assets' in Assets section and return the value for (d). If no value is found, return an empty string.")
    beginning_accounts_payable: str = Field(description="Find 'Accounts Payable' in Liabilities and Capital section and return value for (b). If no value is found, return an empty string.")
    ending_accounts_payable: str = Field(description=" Find 'Accounts Payable' in Liabilities and Capital section and return value for (d). If no value is found, return an empty string.")
    beginning_notes_payable: str = Field(description="Find 'payable in less than 1 year' in Liabilities and Capital section and return the value for (b). If no value is found, return an empty string.")
    ending_notes_payable: str = Field(description="Find 'payable in less than 1 year' in Liabilities and Capital section and return the value for (d). If no value is found, return an empty string.")
    beginning_other_current_liabilities: str = Field(description="Find 'Other current liabilities' in Liabilities and Capital section and return the value for (b). If no value is found, return an empty string.")
    ending_other_current_liabilities: str = Field(description="Find 'Other current liabilities' in Liabilities and Capital section and return the value for (d). If no value is found, return an empty string.")
    beginning_total_liabilities: str = Field(description="Find 'Total Liabilities and Shareholder Equity' in Liabilities and Capital section and return the value for (b). If no value is found, return an empty string.")
    ending_total_liabilities: str = Field(description="Find 'Total Liabilities and Shareholder Equity' in Liabilities and Capital section and return the value for (d). If no value is found, return an empty string.")


class F1040_p1(BaseModel):
    """Extract the form number, fiscal start date, fiscal end date, and the plan liabilities beginning of the year and end of the year."""
    form_number: str = Field(description="The Form Number")
    tax_year: str = Field(description="The tax year of this form")
    primary_first_name: str = Field(description="The first name of the primary tax payer")
    primary_last_name: str = Field(description="The last name of the primary tax payer")
    # primary_ssn: bool = Field(description="Whether there is an SSN present in the SSN field.")
    # primary_ssn: str = Field(description="The first 6 digits of the SSN number of the primary tax payer.")
    primary_ssn_last_4: str = Field(description="Only the last 4 digits of the SSN number of the primary tax payer.")
    spouse_first_name: str = Field(description="The first name of the spouse. If not provided, please return an empty string.")
    spouse_last_name: str = Field(description="The first name of the spouse. If not provided, please return an empty string.")
    # spouse_ssn: str = Field(description="The first 6 digits of the SSN of the spouse. If not provided, please return an empty string.")
    spouse_ssn_last_4: str = Field(description="Only the last 4 digits of the SSN of the spouse. If not provided, please return an empty string.")
    full_address: str = Field(description="The street address of the taxpayer.")
    full_address: str = Field(description="The city, state, zip of the taxpayer.")
    w2_wages: str = Field(description="The total amount from Form W2 on line 1a. May be empty. Return an empty string if no values found on line.")
    agi: str = Field(description="Adjusted gross income for the year. May be empty. Return an empty string if no values found on line.")

class F1040_sch_c(BaseModel):
    tax_year: str = Field(description="Tax year of the form")
    owner_name: str = Field(description="Name of proprietor")
    business_name: str = Field(description="Business name")
    street_address: str = Field(description="Business address suite")
    city_state: str = Field(description="City, town, or post office")
    # primary_ssn: str = Field(description="The first 6 digits of the SSN number of the primary tax payer.")
    ssn_last_4: str = Field(description="The last 4 digits of the SSN number of the primary tax payer.")
    ein: str = Field(description="The employer ID Number (EIN) of the entity")
    gross_revenue: str = Field(description="Gross Receipts or Sales on Line 1. May be empty. Return an empty string if no values found on line.")
    cost_of_goods_sold: str = Field(description="Cost of Goods Sold. May be empty. Return an empty string if no values found on line.")
    gross_profit: str = Field(description="Gross Profit. May be empty. Return an empty string if no values found on line.")
    depreciation: str = Field(description="Depreciation and other expenses. May be empty. Return an empty string if no values found on line.")
    interest_mortgage: str = Field(description="Mortgage interest paid to banks. May be empty. Return an empty string if no values found on line.")
    interest_other: str = Field(description="'Other' listed under Interest. May be empty. Return an empty string if no values found on line.")
    taxes_licenses: str = Field(description="Taxes and licenses. May be empty. Return an empty string if no values found on line.")
    total_deductions: str = Field(description="Total Expenses before net profit calculation. May be empty. Return an empty string if no values found on line.")
    net_profit: str = Field(description="Tentative profit or loss. May be empty. Return an empty string if no values found on line.")

class F1120S_p1(BaseModel):
    tax_year: str = Field(description="Calendar Year or tax year")
    business_name: str = Field(description="Name of the corporation or entity.")
    street_address: str = Field(description="Street address of corporation or entity.")
    city_state: str = Field(description="City, state, zip of the coroporation or entity.")
    ein: str = Field(description="Employer Identification Number of the corporation or entity.")
    inception_date: str = Field(description="Date Incorporated")
    gross_revenue: str = Field(description="Gross receipts or sales in the far right column. If no value is found, return an empty string.")
    cost_of_goods_sold: str = Field(description="Cost of goods sold label")
    gross_profit: str = Field(description="'Gross Profit' label.")
    officers_compensation: str = Field(description="Officers Compensation. If no value is found, return an empty string.")
    interest: str = Field(description="Interest paid. If no value is found, return an empty string.")
    depreciation: str = Field(description="Depreciation. If no value is found, return an empty string.")
    total_deductions: str = Field(description="Total deductions, right above ordinary business profit. If confidence is less than 0.9, return an empty string.")
    net_profit: str = Field(description="Ordinary Business profit. If no value is found, return an empty string.")

class F1120_p1(BaseModel):
    tax_year: str = Field(description="Calendar Year or tax year")
    business_name: str = Field(description="Name of the business or entity.")
    street_address: str = Field(description="Number street and room label.")
    city_state: str = Field(description="City or town, state")
    ein: str = Field(description="Employer Identification Number")
    inception_date: str = Field(description="Date Incorporated")
    gross_revenue: str = Field(description="Value of 'Balance' under 'Gross receipts or sales' section. If no value is found, return an empty string.")
    cost_of_goods_sold: str = Field(description="Cost of goods sold. If no value is found, return an empty string.")
    gross_profit: str = Field(description="Gross Profit. If no value is found, return an empty string.")
    officers_compensation: str = Field(description="Officers Compensation. If no value is found, return an empty string.")
    interest: str = Field(description="Interest paid. If no value is found, return an empty string.")
    depreciation: str = Field(description="Depreciation from Form")
    total_deductions: str = Field(description="Total deductions label.")
    net_profit: str = Field(description="Taxable income before")

class F1065_p1(BaseModel):
    tax_year: str = Field(description="Calendar Year or tax year")
    business_name: str = Field(description="Name of partnership")
    street_address: str = Field(description="Street address of partnership.")
    city_state: str = Field(description="City or town, state of partnership.")
    ein: str = Field(description="Employer Identification Number of partnership.")
    inception_date: str = Field(description="Date Business Started or Inception Date")
    gross_revenue: str = Field(description="Value of 'Balance' under 'Gross receipts or sales' section. If no value is found, return an empty string.")
    cost_of_goods_sold: str = Field(description="Cost of goods sold. If no value is found, return an empty string.")
    gross_profit: str = Field(description="Gross Profit. If no value is found, return an empty string.")
    officers_compensation: str = Field(description="Guaranteed payments to partners. If no value is found, return an empty string.")
    interest: str = Field(description="Interest paid. If no value is found, return an empty string.")
    depreciation: str = Field(description="Value of 'Less depreciation reported on Form 1125' on the right most part of the table. If no value is found, return an empty string.")
    total_deductions: str = Field(description="Total deductions. If no value is found, return an empty string.")
    net_profit: str = Field(description="Ordinary Business profit. If no value is found, return an empty string.")

class F1065_k1(BaseModel):
    tax_year: str = Field(description="For calendar year, or tax year label")
    business_ein: str = Field(description="Employer Identification Number of the partnership")
    business_name: str = Field(description="Partnership's name, address, city")
    ssn_last_4: str = Field(description="Only last 4 digits of SSN")
    shareholder_name: str = Field(description="Name, address, city, state for partner")
    ownership_pct: str = Field(description="Ending ownership percentage based on profit")

class F1120S_k1(BaseModel):
    tax_year: str = Field(description="Tax year of the form ")
    business_ein: str = Field(description="Employer Identification Number of the corporation")
    business_name: str = Field(description="Name of the corporation in 'Corporations name' field")
    ssn_last_4: str = Field(description="Only last 4 digits of SSN")
    shareholder_name: str = Field(description="Shareholder's name, as indicate in the Shareholder name field")
    ownership_pct: str = Field(description="Current year allocation percentage %")

class Acord28(BaseModel):
    certificate_date: str = Field(description="Date that certificate was issued, found at top of page. Return an empty string if no values found.")
    named_insured_name: str = Field(description="Name of person or entity as shown in 'Named Insured' field. Return an empty string if no values found.")
    named_insured_address: str = Field(description="Full address of person or entity as shown in 'Named Insured' field. Return an empty string if no values found.")
    property_address: str = Field(description="Full address shown person or entity as shown in 'Location/Description' field in the Property Information section. Return an empty string if no values found.")
    effective_date: str = Field(description="Effective date. May be empty, so return an empty string if field is empty.")
    expiration_date: str = Field(description="Expiration date. May be empty, so return an empty string if field is empty.")
    property_coverage_amount: str = Field(description="Commercial Property Coverage Amount. May be empty, so return an empty string if field is empty.")
    policy_deductible: str = Field(description="Policy deductible of commercial property. May be empty, so return an empty string if field is empty.")
    additional_interest_name: str = Field(description="Name of Additional Interest, as shown in 'Name and address' field in Additional Interest section. May be empty, so return an empty string if field is empty.")
    additional_interest_address: str = Field(description="Address of Additional Interest, as shown in 'Name and address' field in Additional Interest section. May be empty, so return an empty string if field is empty.")
    lenders_loss_payable: str = Field(description="The value inside checkbox for the label 'Lenders Loss Payable'. This may be blank, or have a character like 'x' or checkmark. May be empty, so return an empty string if field is empty.")
    business_personal_property: str = Field(description="The value inside checkbox for the label 'Business Personal Property'. This may be blank, or have a character like 'x' or checkmark. May be empty, so return an empty string if field is empty.")

class Acord25(BaseModel):
    certificate_date: str = Field(description="Date that certificate was issued, found at top of page. Return an empty string if no values found.")
    named_insured_name: str = Field(description="Name of person or entity as shown in 'Insured' field. Return an empty string if no values found.")
    named_insured_address: str = Field(description="Full address of person or entity as shown in 'Insured' field. Return an empty string if no values found.")
    property_address: str = Field(description="Full address shown person or entity as shown in 'Location/Description' field in the Property Information section. Return an empty string if no values found.")
    effective_date: str = Field(description="General Liability Effective date. May be empty, so return an empty string if field is empty.")
    expiration_date: str = Field(description="General Liability Expiration date. May be empty, so return an empty string if field is empty.")
    general_liability_limit_per_occurrence: str = Field(description="'Each Occurrence' value for General Liability policy. May be empty, so return an empty string if field is empty.")
    general_liability_check: str = Field(description="Value inside checkbox for 'Commercial General Liability'. This may be blank, or have a character like 'x' or checkmark. Return empty string if field is empty.")
    certificate_holder_name: str = Field(description="Name of Certificate Holder, as shown in 'Name and address' field in Certificate Holder section. May be empty, so return an empty string if field is empty.")
    certificate_holder_address: str = Field(description="Address of Certificate Holder, as shown in 'Name and address' field in Certificate Holder section. May be empty, so return an empty string if field is empty.")
    lenders_loss_payable: bool = Field(description="Whether the Description of Operations indicates that the certificate holder is 'Lenders Loss Payable'.")

# Empty classes for unspecified document types
class DriversLicense(BaseModel):
    first_name: str = Field(description="First name of the person on the driver's license.")
    last_name: str = Field(description="Last name of the person on the driver's license.")
    exp_date: str = Field(description="Expiration date of the driver's license.")
    dob: str = Field(description="Date of birth of the person on the driver's license.")

class Passport(BaseModel):
    first_name: str = Field(description="First name of the person on the passport.")
    last_name: str = Field(description="Last name of the person on the passport.")
    exp_date: str = Field(description="Expiration date of the passport.")
    dob: str = Field(description="Date of birth of the person on the passport.")

class LeaseDocument(BaseModel):
    renter_name: str = Field(description="Name of the renter or lessee on the lease. If no value is found, return an empty string.")
    lease_start_date: str = Field(description="Start date of the lease. If no value is found, return an empty string.")
    lease_end_date: str = Field(description="End date of the lease. If no value is found, return an empty string.")
    term_length: str = Field(description="Length of the lease term. If no value is found, return an empty string.")

class CertificateOfGoodStanding(BaseModel):
    business_name: str = Field(description="Name of the business on the certificate.")
    current_standing: str = Field(description="Current standing of the business.")
    date_incorporated: str = Field(description="Date the business was incorporated or started.")

class BusinessLicense(BaseModel):
    business_name: str = Field(description="Name of the business on the license.")
    current_standing: str = Field(description="Current standing of the license.")


# Mapping function
def get_model(model_name: str) -> Type[BaseModel]:
    model_mapping = {
        "1120S_p1": F1120S_p1,
        "1120S_k1": F1120S_k1,
        "1120S_bal_sheet": BalanceSheet,
        "1065_p1": F1120S_p1,
        "1065_k1": F1065_k1,
        "1065_bal_sheet": BalanceSheet,
        "1120_p1": F1120S_p1,
        "1120_bal_sheet": BalanceSheet,
        "1040_p1": F1040_p1,
        "1040_sch_c": F1040_sch_c,
        "acord_25": Acord25,
        "acord_28": Acord28,
        "unknown": None,
        "unknown_text_type": None,
        "unknown_tax_form_type": None,
        "drivers_license": DriversLicense,
        "passport": Passport,
        "lease_document": LeaseDocument,
        "certificate_of_good_standing": CertificateOfGoodStanding,
        "business_license": BusinessLicense,
    }
    return model_mapping.get(model_name)

def extract_structured_data(file_path: str, model: BaseModel):
    # Upload the file to the File API
    file = client.files.upload(file=file_path, config={'display_name': file_path.split('/')[-1].split('.')[0]})
    # Generate a structured response using the Gemini API
    prompt = f"Extract the structured data from the following PDF file"
    response = client.models.generate_content(model=model_id, contents=[prompt, file], config={'response_mime_type': 'application/json', 'response_schema': model})
    print(response)
    if response:
        # Get relevant information from the response
        info = {}
        info['filename'] = file_path
        info['model_version'] = response.model_version
        usage_info = response.usage_metadata
        info.update(usage_info)
        info = pd.json_normalize(info)
        # Make line items into dataframe in key value pairs
        line_items = response.parsed.model_dump()
        extracted = pd.DataFrame()
        extracted['key'] = line_items.keys()
        extracted['value'] = line_items.values()
        extracted['filename'] = file_path
        extracted = extracted[['filename', 'key', 'value']]
        return info, extracted
    return None