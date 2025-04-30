import requests
import json
import tempfile
import os

def test_cv_matching():
    # API endpoint
    url = 'http://localhost:8000/api/match-cv'
    
    # Sample CV file
    cv_content = """# John Doe
Senior Software Engineer

## Experience
- Lead Developer at Tech Corp (2018-Present)
  - Developed scalable web applications using Python and FastAPI
  - Managed team of 5 developers
  - Implemented ML-based recommendation systems

## Skills
- Python, FastAPI, SQL, Machine Learning
- Team Leadership, Project Management
- Cloud Services (AWS, Azure)

## Education
- M.S. Computer Science, Stanford University
- B.S. Software Engineering, MIT
"""
    
    # Optional parameters
    data = {
        'interests': 'machine learning, cloud computing',
        'soft_skills': 'leadership, communication'
    }

    temp_path = None
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as temp_file:
            temp_file.write(cv_content)
            temp_path = temp_file.name

        # Open the temporary file for the request
        with open(temp_path, 'rb') as cv_file:
            files = {
                'cv_file': ('cv.md', cv_file, 'text/markdown')
            }
            
            # Make the request
            response = requests.post(url, files=files, data=data)
            
            # Check if request was successful
            if response.status_code == 200:
                matches = response.json()
                print('\nSuccessful Response!')
                print('\nTop Job Matches:')
                for i, job in enumerate(matches[:3], 1):
                    print(f"\n{i}. {job['job_title']}")
                    print(f"   Match Score: {job['match_score']:.2f}")
                    print(f"   Summary: {job['job_summary'][:200]}...")
            else:
                print(f'Error: {response.status_code}')
                print(response.text)
    except Exception as e:
        print(f'Error: {str(e)}')
    finally:
        # Cleanup temporary file
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == '__main__':
    test_cv_matching()