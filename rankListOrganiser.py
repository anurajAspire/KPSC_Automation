import pdfplumber
import pandas as pd
import re
import os
import json
#it open every ranklist pdf files in the folder, reads and generate rank list in a json file with category name as file name.
#these json files can combine into single or search individually for each candidate.
#or combine restructure these json files in such a way that 26 different files from A-Z bades on candidates name makes search effectively. its easy to apply search as in sorted list.

# --- CONFIGURATION ---
FILE_NAME = "rl_382_2024_00.pdf" 
PDF_FOLDER = "downloaded_pdfs" #keep all psc rank list pdf files here
FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), PDF_FOLDER, FILE_NAME)

# Path Setup
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(SCRIPT_DIR, PDF_FOLDER)
def run_local_analysis():
    """Scans the local folder and extracts data from the PDFs."""
    if not os.path.exists(PDF_PATH):
        print(f"Error: The folder '{LOCAL_PDF_DIR}' was not found in {SCRIPT_DIR}")
        return

    print(f"--- Starting Analysis in: {PDF_PATH} ---")
    all_results = []
    
    # Get all PDF files from the folder
    files = [f for f in os.listdir(PDF_PATH) if f.lower().endswith('.pdf')]
    
    if not files:
        print("No PDF files found in the folder to analyze.")
        return

    for filename in files:
        file_path = os.path.join(PDF_PATH, filename)
        
        # Skip empty or corrupted files (less than 5KB)
        if os.path.getsize(file_path) < 5000:
            print(f" [!] Skipping {filename}: File is too small/corrupt.")
            continue

        print(f" Analyzing: {filename}")
        analyze_dynamic_columns(file_path) #comment to execute single file.
        
def analyze_dynamic_columns(path):
    if not os.path.exists(path):
        print(f"Error: File not found at {path}")
        return

    results = []
    
    # Settings tuned for KPSC tabular alignment
    table_settings = {
        "vertical_strategy": "text", 
        "horizontal_strategy": "text",
        "snap_y_tolerance": 4,
        "intersection_x_tolerance": 15
    }

    try:
        with pdfplumber.open(path) as pdf:
            current_cat = "Unknown"
            current_list_type = "Main List"
            current_group = "GENERAL"
            
            text_all =[]
            post_cat = "000/0000"
            #cat_no_match = re.search(r"Cat\.No\.(\d+/\d+)", raw_text)
            #cat_no = cat_no_match.group(1) if cat_no_match else "Unknown"
            
            numberTotalCandidate = 0
            #word_count = 0
            #words = []
            for page in pdf.pages:
                text = page.extract_text(x_tolerance=2) or ""
                cat_match = re.search(r"Cat\.?\s*No\.?\s*:\s*(\d+/\d+)", text)
                
                #header_match = re.search(r"Rank\s+.*?\s+Remarks", text)
                #if header_match:
                    #extracted_text = header_match.group(0)
                    # 2. Count the words
                    # .split() splits by any whitespace and removes empty strings
                    #words = extracted_text.split()
                    #word_count = len(words)
                    #print(f"Extracted: '{extracted_text}'")
                    #print(f"Word Count: {word_count}")
                    #print(f"Individual Words: {words}")
                
                matchTotalCandidate = re.search(r"Total number of Candidates in the Ranked List\s+(\d+)", text)
                if matchTotalCandidate:
                    numberTotalCandidate = matchTotalCandidate.group(1) # Result: "150"
                    #print(numberTotalCandidate)
                    
                
                if cat_match:
                    current_cat = cat_match.group(1)
                    #break
                #print(text)
                text_all.append(text)
                #start, end = "This Ranked List is brought into force with effect from", "Ranked List"
                #result = text.split(start)[1].split(end)[0].strip()
                #print(f"{start}\n{result}")
                
                
        start, end = "force with effect from", "Total number of Candidates in the Ranked List"
        #result = text_all.split(start)[1].split(end)[0].strip()
        # Convert the list into one giant string
        combined_text = "\n".join(text_all)
        # Now findall will work perfectly
        root_key = f"{re.findall(r"Cat\.?\s*No\.?\s*:\s*(\d+/\d+)", combined_text)}"
        
        result = "\n".join(text_all).split(start)[1].split(end)[0].strip()
        #print(f"\n{result}")
        
        def extract_to_clean_json(raw_text):
            
            # Pattern to match candidate rows
            #row_pattern = r"^(\d+)\s+(\d+)\s+([A-Z\s.]{3,})\s+[\d.]+\s+[\d.]+(?:\s+[\d.]+)?\s+[\d.]+\s+(\d{2}/\d{2}/\d{4})\s*(.*)"
            #row_pattern = r"^(\d+)\s+(\d+)\s+([A-Z\s.]{3,})\s+(?:[\d.-]+\s+)+(\d{2}/\d{2}/\d{4})\s*(.*)"
            COMMY_KEYWORDS = {
                'EZHAVA', 'OBC', 'MUSLIM', 'SC', 'ST', 'LA', 'AI', 'LC', 
                'EZHA', 'OB-C', 'V-VISWAKARMA', 'SCCC', 'DHEEVARA', 'H-NADAR'
            }
            #row_pattern = r"^(\d+)(?:\s+(\d+))?\s+([a-zA-Z\s\.]+?)\s*(?=\d)(.*?)\s*(\d{2}/\d{2}/\d{4})(?:\s+([a-zA-Z-]+))?(?:\s+([a-zA-Z\s.,-]+))?$"
            row_pattern = r"^(\d+)(?:\s+(\d+))?\s*([a-zA-Z\s\.']+?)\s*(?=\d)(.*?)\s*(\d{2}/\d{2}/\d{4})(?:\s*([a-zA-Z\[-]+))?(?:\s+([a-zA-Z\s.,-/]+))?$"
                        # --- DEFINING ROW PATTERNS ---
            # Pattern 1: Rank, Sl., Name, Test, Int, Wtg, Total, DOB, Commy, Remarks
            # captures: Rank(1), Sl(2), Name(3), DOB(4), Commy/Remarks(5)
            #PATTERN_A = r"^(\d+)\s+(\d+)\s+([A-Z\s.]{3,})\s+[\d.-]+\s+[\d.-]+\s+[\d.-]+\s+[\d.-]+\s+(\d{2}/\d{2}/\d{4})\s*(.*)"
            # Pattern 2: Rank, Reg.No, Name, Test, Wtg, Total, DOB, Commy, Remarks
            #PATTERN_B = r"^(\d+)\s+(\d{6})\s+([A-Z\s.]{3,})\s+[\d.-]+\s+[\d.-]+\s+[\d.-]+\s+(\d{2}/\d{2}/\d{4})\s*(.*)"
            # Pattern 3: Rank, Sl., Name, DOB, Commy, Remarks
            #PATTERN_C = r"^(\d+)\s+(\d+)\s+([A-Z\s.]{3,})\s+(\d{2}/\d{2}/\d{4})\s*(.*)"
            
            supplementary_categories = [
                "Ezhava/Thiyya/Billava", "Scheduled Caste", "Scheduled Tribe", 
                "Muslim", "Latin Catholics/A.I", "OBC", "Viswakarma", 
                "SIUC Nadar", "Scheduled Caste Converts to Christianity", 
                "Dheevara", "Hindu Nadar", "Economically Weaker Section", "Low Vision", "Deaf & Hard of Hearing", "Locomotor Disability", "AS(M),ID(M),SLD,MI"
            ]
            
            candidates = []
            current_list_type = "Main"
            current_sub_category = None
            
            lines = raw_text.split('\n')
            #print(lines)
            for line in lines:
                line = line.strip()
                if not line: continue
                    
                # Switch to Supplementary mode
                if "Supplementary List" in line:
                    current_list_type = "Supplementary"
                    continue

                # Detect specific sub-category within Supplementary List
                for cat in supplementary_categories:
                    if cat.lower() in line.lower():
                        current_sub_category = cat
                        break
                
                # Match candidate data
                # --- DATA ROW MATCHING ---
                #match_a = re.match(PATTERN_A, line)
                #match_b = re.match(PATTERN_B, line)
                #match_c = re.match(PATTERN_C, line)
                #match = match_a or match_b or match_c
                #print(line)
                
                #match = re.match(row_pattern, line)
                match = re.search(row_pattern, line.strip())
                if match:
                    rank_val = match.group(1)
                    rank, sl_no, name, extra, dob, c_raw, r_raw = match.groups()
                    #Logic to handle different group counts based on which pattern matched")
                    # We use specific indices based on the regex groups defined above
                    #if match_a: # Rank, Sl, Name, DOB, Rest
                    #    rank, id_no, name, dob, rest = match_a.groups()
                    #elif match_b: # Rank, RegNo, Name, DOB, Rest
                    #    rank, id_no, name, dob, rest = match_b.groups()
                    #else: # Pattern C: Rank, Sl, Name, DOB, Rest
                    #    rank, id_no, name, dob, rest = match_c.groups()
                            
                    commy = None
                    remarks = None
            
                    if c_raw:
                        if c_raw.upper() in COMMY_KEYWORDS or '-' in c_raw:
                            commy = c_raw
                            remarks = r_raw.strip() if r_raw else None
                        else:
                            # Otherwise, the whole ending is a Remark
                            remarks = f"{c_raw} {r_raw or ''}".strip()

                    # Base dictionary with common fields
                    candidate_obj = {
                        "rank": f"SL-{rank_val}" if current_list_type == "Supplementary" else rank_val,
                        #"name": match.group(3).strip(),
                        "name": name.strip(),
                        "dob": dob,
                        #"dob": match.group(4),
                        #"community": match.group(5).strip(),
                        "community": commy,
                        "list_type": current_list_type,
                        "remarks": remarks
                    }
                    
                    # Only add supplementary_type if it's NOT the Main List
                    if current_list_type == "Supplementary":
                        candidate_obj["supplementary_type"] = current_sub_category
                        
                    candidates.append(candidate_obj)
            entry_count = len(candidates)
            #print(f"Total Candidates in List: {entry_count}")
            #print(numberTotalCandidate)
            if(int(numberTotalCandidate) != int(entry_count)):
                print("Error : Missed some candidates")
            final_output = {root_key: candidates}     
            # Count the entries
            
            
            return final_output

        # Generate data
        data_list = extract_to_clean_json(result)
        #print(data_list)
        # Convert to JSON string (uses double quotes by default)
        json_output = json.dumps(data_list, indent=4)
        
        #print(json_output)
        # Save to file
        safe_filename = re.sub(r'[^\w\s-]', '_', root_key).replace(' ', '_')
        with open(f"category_{safe_filename}.json", 'w', encoding='utf-8') as f:
            f.write(json_output)

        print(f"JSON file category_{safe_filename}.json has been created.")        
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_dynamic_columns(FILE_PATH)
    run_local_analysis()
