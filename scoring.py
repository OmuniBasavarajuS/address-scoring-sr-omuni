#!/usr/bin/env python
# coding: utf-8

import csv
import re

# Define the list of special characters and words
special_chars = [',', '-', ':', "'", '#']

highPriorityWords = ["no", "nagar", "landmark", "floor", "colony", "flat", "sector",
                     "house", "opp", "school", "hospital", "bank", "layout", "society",
                     "post", "mandir", "tower", "building", "store", "office", "home",
                     "beside", "temple", "flr", "off", "nd", "th", "near", "new", 
                     "plot", "plt", "park", "opposite", "vihar", "behind"]

lowPriorityWords = ["cross", "cr", "street", "st", "apartment", "apt", "lane", "ln",
                    "stage", "stg", "phase", "ph", "block", "blk", "division", "road", "rd"]



# Functions to read city and pincode data from individual and consolidated CSV files
def read_data(file_path):
    data = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            data.append(row[0].upper())
    return data

def read_city_pincode_data(file_path):
    city_pincode_data = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            city = row[0].upper()
            pincode = row[1]
            city_pincode_data.append((city, pincode))
    return city_pincode_data

# Function to extract pincode from the address
def extract_pincode(address):
    pincode_pattern = r'\b\d{6}\b'
    matches = re.findall(pincode_pattern, address)
    return matches[0] if matches else None

# Scoring function with pincode extraction and verification
def score_address(address, cities, pincodes, consolidated_data):
    score = 0
    messages = []  # List to store messages
    upper_address = address.upper()

    messages.append("Starting address scoring...")
    messages.append(f"Address:, {address}")

    # Extract and check pincode from the address
    extracted_pincode = extract_pincode(upper_address)
    if extracted_pincode:
        messages.append(f"Extracted Pincode: {extracted_pincode}")
        if len(extracted_pincode) not in [6]:
            messages.append("Warning: Extracted pincode length is not standard.")
        # Check if the extracted pincode is in the master pincode file
        if extracted_pincode not in pincodes:
            messages.append(f"Pincode {extracted_pincode} does not exist in the master pincode file.")

    # Assign a maximum score for each component
    max_score_special_chars = 5  # Max score assignable for special characters
    max_score_high_priority_words = 30  # Higher score for high-priority words
    max_score_low_priority_words = 10    # Lower score for low-priority words
    max_score_city = 10           # Max score for city
    max_score_pincode = 10        # Max score for pincode
    max_score_both = 35           # Max score if both city and pincode are found

    # Check for special characters
    special_char_count = sum(upper_address.count(char) for char in special_chars)
    if special_char_count > 0:
        score += max_score_special_chars
        if special_char_count > 0:
            messages.append(f"Special character found {special_char_count}")
    
    # Negative weightage for repeating letters and numbers in series
    negative_weightage_repeating_letters = 30
    negative_weightage_numbers_in_series = 55
    negative_weightage_alphabetical_series = 70

    # Check for repeating letters (more than 3 times consecutively)
    if re.search(r"(.)\1{3,}", upper_address):
        score -= negative_weightage_repeating_letters
        print("Repeating letters found in the address.")

    # Check for numbers in series (more than 6 digits)
    if re.search(r"0123456|1234567|2345678|3456789|9876543|8765432|7654321|6543210", upper_address):
        score -= negative_weightage_numbers_in_series
        print("Numbers in series found in the address.")
    
    # Check for alphabetical series longer than 4 characters
    if re.search(r"(?=(A(?=B(?=C(?=D(?=E))))))|(?=(B(?=C(?=D(?=E(?=F))))))|(?=(C(?=D(?=E(?=F(?=G))))))|(?=(D(?=E(?=F(?=G(?=H))))))|(?=(E(?=F(?=G(?=H(?=I))))))|(?=(F(?=G(?=H(?=I(?=J))))))|(?=(G(?=H(?=I(?=J(?=K))))))|(?=(H(?=I(?=J(?=K(?=L))))))|(?=(I(?=J(?=K(?=L(?=M))))))|(?=(J(?=K(?=L(?=M(?=N))))))|(?=(K(?=L(?=M(?=N(?=O))))))|(?=(L(?=M(?=N(?=O(?=P))))))|(?=(M(?=N(?=O(?=P(?=Q))))))|(?=(N(?=O(?=P(?=Q(?=R))))))|(?=(O(?=P(?=Q(?=R(?=S))))))|(?=(P(?=Q(?=R(?=S(?=T))))))|(?=(Q(?=R(?=S(?=T(?=U))))))|(?=(R(?=S(?=T(?=U(?=V))))))|(?=(S(?=T(?=U(?=V(?=W))))))|(?=(T(?=U(?=V(?=W(?=X))))))|(?=(U(?=V(?=W(?=X(?=Y))))))|(?=(V(?=W(?=X(?=Y(?=Z))))))", upper_address):
        score -= negative_weightage_alphabetical_series
        print("Alphabetical series longer than 4 characters found in the address.")

    # Additional weightage parameters
    positive_weightage_small_number = 25
    negative_weightage_no_small_number = 80

    # Check for numbers less than 5 digits
    if re.search(r"\b\d{1,4}\b", upper_address):
        score += positive_weightage_small_number
        print("Number with less than 5 digits found in the address.")
    else:
        score -= negative_weightage_no_small_number
        print("No number with less than 5 digits found in the address.")
    
    # Additional weightage parameters
    positive_weightage_number_prefix = 10
    negative_weightage_suffix_without_number = 40
    positive_weightage_number_and_suffix = 35

    # Check for numbers not greater than 4 digits preceded by #, No, or Number
    if re.search(r"(#|NO|NUMBER|NO.|NO )\s*\d{1,4}", upper_address):
        score += positive_weightage_number_prefix
        print("Number preceded by #, No, or Number found in the address.")

    # Check for 'th', 'rd' not preceded by numbers
    if re.search(r"\b(?<!\d)(ST|TH|RD)\b", upper_address):
        score -= negative_weightage_suffix_without_number
        print("'st', th' or 'rd' found in the address without preceding numbers.")

    # Check for words like 'Main', 'Road', 'Cross', 'Street' preceded by number and 'th', 'rd'
    if re.search(r"\d{1,4}(ST|TH|RD)\s+(MAIN|ROAD|CROSS|STREET|ST.|RD.)", upper_address):
        score += positive_weightage_number_and_suffix
        print("Words like 'Main', 'Road', 'Cross', 'Street' preceded by number and 'th', 'rd' found in the address.")

   # Split address into individual components for better matching
    address_components = re.findall(r'\b\w+\b', upper_address)


    # Check for high and low priority words
    high_priority_found = any(word.upper() in address_components for word in highPriorityWords)
    low_priority_found = any(word.upper() in address_components for word in lowPriorityWords)

    if high_priority_found:
        score += max_score_high_priority_words
        messages.append("High-priority words found in the address.")
    else:
        messages.append("No high-priority words found in the address.")

    if low_priority_found:
        score += max_score_low_priority_words
        messages.append("Low-priority words found in the address.")
    else:
        messages.append("No low-priority words found in the address.")

    # Check for city and pin code
    city_found = any(city in upper_address for city in cities)
    pincode_found = any(pincode in upper_address for pincode in pincodes)

    if city_found:
        score += max_score_city
        messages.append("City found in the address.")

    if pincode_found:
        score += max_score_pincode
        messages.append("Pincode found in the address.")

    # Additional score if both city and pincode are found
    for city, pincode in consolidated_data:
        if city in upper_address and pincode in upper_address:
            score += max_score_both  # Additional score for both city and pincode match
            messages.append(f"Both city '{city}' and pincode '{pincode}' found together")
            break


    # Check if extracted pincode matches any in the consolidated data
    pincode_match_found = False
    for city, pincode in consolidated_data:
        if extracted_pincode == pincode:
            pincode_match_found = True
            break

    if extracted_pincode and not pincode_match_found:
        messages.append(f"Pincode {extracted_pincode} exists but does not match any city-pincode combination.")

    return min(score, 100), messages

#Function to initialize and score the address
def initialize_and_score(input_address):
    # Paths to the CSV files
    city_file_path = 'master_city_names.csv'  # Adjust the path as necessary
    pincode_file_path = 'master_pincodes.csv'  # Adjust the path as necessary
    consolidated_file_path = 'india_city_pincodes_consolidated.csv'  # Adjust the path as necessary

    # Read data from CSV files
    cities = read_data(city_file_path)
    pincodes = read_data(pincode_file_path)
    consolidated_city_pincode_data = read_city_pincode_data(consolidated_file_path)

    # Score the input address
    address_score, messages = score_address(input_address, cities, pincodes, consolidated_city_pincode_data)
    return address_score, messages