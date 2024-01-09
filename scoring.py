#!/usr/bin/env python
# coding: utf-8

import csv
import re

# Define the list of special characters and words
special_chars = [',', '-', ':', "'", '#']

lowPriorityWords = ["no", "nagar", "landmark", "floor", "colony", "flat", "sector",
                     "house", "opp", "school", "hospital", "bank", "layout", "society",
                     "post", "mandir", "tower", "building", "store", "office", "home",
                     "beside", "temple", "flr", "off", "nd", "th", "near", "new", 
                     "plot", "plt", "park", "opposite", "vihar", "behind","nd","college",
                     "university"]

highPriorityWords = ["cross", "cr", "street", "st", "apartment", "apt", "lane", "ln",
                    "stage", "stg", "phase", "ph", "block", "blk", "division", "road", "rd"]

#lowPriorityWords,highPriorityWords

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
def score_address(address, cities, pincodes, consolidated_data, highPriorityWords, lowPriorityWords, special_chars):
    score = 0  # Starting with a full score
    messages = []  # List to store messages
    upper_address = address.upper()

    messages.append("Starting address scoring...")
    messages.append(f"Address: {address}")

    # Extract and check pincode from the address(+-60)
    extracted_pincode = extract_pincode(upper_address)
    if extracted_pincode:
        messages.append(f"Extracted Pincode: {extracted_pincode}")
        if len(extracted_pincode) == 6:
            if extracted_pincode in pincodes:
                score += 50  # Increase score by 50
                messages.append("Pincode exist in the master file.")
                city_match = any(city in upper_address for city, pin in consolidated_data if pin == extracted_pincode)
                if city_match:
                    score += 10 # Increase score by 60
                    messages.append("Correct Pincode and City mapping.")
                else:
                    score -= 20  # Reduce score by 20
                    messages.append("Incorrect Pincode and City mapping.")
            else:
                messages.append("Pincode does not exist in the master file.")
        else:
            score -= 60  # Reduce score by 60
            messages.append("Pincode length is not standard.")
    else:
        score -= 60  # Reduce score by 50
        messages.append("Pincode not found in the address.")

    # Check for unwanted patterns (-30)
    negative_weightage_patterns = 0
    if re.search(r"(.)\1{3,}", upper_address):
        negative_weightage_patterns += 10  # Adjust weightage as needed
        messages.append("Repeating letters found in the address.")
    if re.search(r"0123456|1234567|2345678|3456789|9876543|8765432|7654321|6543210", upper_address):
        negative_weightage_patterns += 10
        messages.append("Numbers in series found in the address.")
    if re.search(r"(?=(A(?=B(?=C(?=D(?=E))))))|(?=(Z(?=Y(?=X(?=W(?=V))))))", upper_address):
        negative_weightage_patterns += 10
        messages.append("Alphabetical series found in the address.")
    
    score -= negative_weightage_patterns

    # Check for high and low priority words(+-30)
    address_components = re.findall(r'\b\w+\b', upper_address)
    high_priority_count = sum(word.upper() in address_components for word in highPriorityWords)
    low_priority_count = sum(word.upper() in address_components for word in lowPriorityWords)

    if high_priority_count > 1:
        score += 20  # Full weightage for multiple high-priority words
        messages.append(f"{high_priority_count} high-priority words found in the address.")
    elif high_priority_count == 1:
        score += 5  # Half weightage for a single high-priority word
        messages.append("1 high-priority word found in the address.")
    else:
        score -= 30  # Negative weightage for no high-priority words
        messages.append("No high-priority words found in the address.")

    if low_priority_count > 1:
        score += 10  # Full weightage for multiple high-priority words
        messages.append(f"{low_priority_count} low-priority words found in the address.")
    elif low_priority_count == 1:
        score += 5  # Half weightage for a single high-priority word
        messages.append("1 low-priority word found in the address.")
    else:
        score -= 5  # Negative weightage for no high-priority words
        messages.append("No low-priority words found in the address.")

    # Adjust score to ensure it's within 0-100 range and meets the 90+ condition if all criteria are met
    score = max(0, min(score, 100))
    #if score < 90 and all([extracted_pincode, city_match, not negative_weightage_patterns, high_priority_count]):
    #    score = 90

    return score, messages

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
    address_score, messages = score_address(input_address, cities, pincodes, consolidated_city_pincode_data, highPriorityWords, lowPriorityWords, special_chars)
    return address_score, messages