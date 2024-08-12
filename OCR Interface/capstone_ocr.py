from google.api_core.client_options import ClientOptions
from google.cloud import documentai  # type: ignore

import re
import json

# Set the project and processor details as constants
PROJECT_ID = "capstone-project-427415"
LOCATION = "us"
PROCESSOR_DISPLAY_NAME = "projects/661952623985/locations/us/processors/b302abd739961082"

def process_document(file):
    """Process a document image and extract text using Google Document AI.

    Args:
        file: A file-like object or a file path of the document image to process.
    """
    opts = ClientOptions(api_endpoint=f"{LOCATION}-documentai.googleapis.com")
    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    # Check if the input is a file-like object or a string
    if isinstance(file, str):
        # If it's a string, open the file to read the content
        with open(file, "rb") as image_file:
            image_content = image_file.read()
    else:
        # If it's a file-like object, read the content directly
        image_content = file.read()

    raw_document = documentai.RawDocument(
        content=image_content,
        mime_type="image/jpeg",  # Supported file types: https://cloud.google.com/document-ai/docs/file-types
    )

    request = documentai.ProcessRequest(
        name=PROCESSOR_DISPLAY_NAME,
        raw_document=raw_document
    )

    result = client.process_document(request=request)
    document = result.document

    return parse_results(document.text)



def parse_results(text):
    data = {
        "candidate_name": "",
        "results": {}
    }

    # Try multiple patterns to match candidate name
    name_patterns = [
        r"Candidate Name\s*:\s*([^\n]+)",  # Pattern for the format "Candidate Name: Name"
        r"Candidate Name\nType of Examination\nExamination Centre\nCard Details\n\d+\n([^\n]+)",  # Original pattern
        r"Candidate Name\n([^\n]+)\nType of Examination",  # Pattern for format "Candidate Name\nName\nType of Examination"
        r"Candidate Name\n([^\n]+)\n"  # Pattern for format "Candidate Name\nName\n"
    ]
    for pattern in name_patterns:
        name_match = re.search(pattern, text)
        if name_match:
            data['candidate_name'] = name_match.group(1).strip()
            break

    # Parsing subjects and grades more intelligently
    try:
        parts = text.split('Results\n')[1].split('\n')
    except IndexError:
        return json.dumps(data, indent=4)

    subjects = []
    grades = []

    for part in parts:
        clean_part = part.strip()
        if re.match(r"^[A-Z]", clean_part) and not re.match(r"^(A1|B2|B3|C4|C5|C6|D7|E8|F9)$", clean_part) and not re.match(r"^(EXCELLENT|VERY GOOD|GOOD|CREDIT|PASS|FAIL)$", clean_part):
            subjects.append(clean_part.replace(' ', '_').replace('(', '').replace(')', '').lower())
        elif re.match(r"^(A1|B2|B3|C4|C5|C6|D7|E8|F9)$", clean_part):
            grades.append(clean_part)

    # Associate subjects with grades
    if len(subjects) > len(grades):
        for i, subject in enumerate(subjects):
            # Prevent index error for grades
            if i < len(grades):
                data['results'][subject] = grades[i]
            else:
                data['results'][subject] = "Grade missing"
    else:
        for subject, grade in zip(subjects, grades):
            data['results'][subject] = grade

    # Remove any subject with "Grade missing" before returning the result
    data['results'] = {k: v for k, v in data['results'].items() if v != "Grade missing"}

    # Handle variations in subject names
    if 'mathematicscore' in data['results']:
        data['results']['mathematics_core'] = data['results'].pop('mathematicscore')

    return json.dumps(data, indent=4)

def count_grades(results):
    """
    Counts the occurrences of each grade in the given results.

    Args:
        results (dict): A dictionary containing the results of the students.

    Returns:
        dict: A dictionary where the keys are the grades and the values are the counts of each grade.
    """
    grades = ['A1', 'B2', 'B3', 'C4', 'C5', 'C6', 'D7', 'E8', 'F9']
    grade_counts = {grade: 0 for grade in grades}
    
    for grade in results.values():
        if grade in grade_counts:
            grade_counts[grade] += 1

    return grade_counts



def assign_core_maths_score(results):
    """
    Assigns a score to the core mathematics grade based on a predefined mapping.

    Args:
        results (dict): A dictionary containing the results of a student.

    Returns:
        int: The assigned score for the core mathematics grade.
    """
    score_mapping = {
        'A1': 10,
        'B2': 8,
        'B3': 6,
        'C4': 4,
        'C5': 2,
        'C6': 1,
        'D7': 0,
        'E8': 0,
        'F9': 0
    }
    
    core_maths_score = 0
    if 'mathematics_core' in results:
        core_maths_grade = results['mathematics_core']
        core_maths_score = score_mapping.get(core_maths_grade, 0)
    
    return core_maths_score


def assign_elective_maths_score(results):
    """
    Assigns a score to the elective maths grade based on a predefined mapping.

    Args:
        results (dict): A dictionary containing the results of a student.

    Returns:
        int: The score assigned to the elective maths grade.
    """
    score_mapping = {
        'A1': 10,
        'B2': 8,
        'B3': 6,
        'C4': 4,
        'C5': 2,
        'C6': 1,
        'D7': 0,
        'E8': 0,
        'F9': 0
    }
    
    elective_maths_score = 0
    if 'mathematicselect' in results:
        elective_maths_grade = results['mathematicselect']
        elective_maths_score = score_mapping.get(elective_maths_grade, 0)
    
    return elective_maths_score


def assign_physics_score(results):
    """
    Assigns a score to the physics grade based on a predefined mapping.

    Args:
        results (dict): A dictionary containing the results of a student.

    Returns:
        int: The assigned score for the physics grade.
    """
    score_mapping = {
        'A1': 10,
        'B2': 8,
        'B3': 6,
        'C4': 4,
        'C5': 2,
        'C6': 1,
        'D7': 0,
        'E8': 0,
        'F9': 0
    }
    
    physics_score = 0
    if 'physics' in results:
        physics_grade = results['physics']
        physics_score = score_mapping.get(physics_grade, 0)
    
    return physics_score


def calculate_aggregate(results):
    score_mapping = {
        'A1': 1,
        'B2': 2,
        'B3': 3,
        'C4': 4,
        'C5': 5,
        'C6': 6,
        'D7': 7,
        'E8': 8,
        'F9': 9
    }
    
    # Required subjects
    required_subjects = ['english_lang', 'mathematics_core', 'integrated_science']
    
    # Other subjects to consider (excluding social studies)
    other_subjects = [subject for subject in results if subject not in required_subjects and subject != 'social_studies']
    
    # Get scores for required subjects
    required_scores = [score_mapping[results[subject]] for subject in required_subjects if subject in results and results[subject] in score_mapping]
    
    # Get scores for other subjects
    other_scores = [score_mapping[results[subject]] for subject in other_subjects if subject in results and results[subject] in score_mapping]
    
    # Sort other scores in ascending order and select the top three
    other_scores.sort()
    best_other_scores = other_scores[:3]
    
    # Calculate the total aggregate
    total_aggregate = sum(required_scores + best_other_scores)
    
    return total_aggregate



def assign_score(aggregate):
    if 6 <= aggregate <= 9:
        return 30
    elif 10 <= aggregate <= 12:
        return 25
    elif 13 <= aggregate <= 15:
        return 20
    elif 16 <= aggregate <= 19:
        return 15
    elif 20 <= aggregate <= 24:
        return 10
    elif aggregate >= 25:
        return 5
    else:
       # Return 0 if the aggregate doesn't fall within any of the defined ranges 
        return 0 
