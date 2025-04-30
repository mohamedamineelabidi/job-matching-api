from add_data_to_db import JobEmbeddingStore

def add_test_jobs():
    # Initialize the store
    store = JobEmbeddingStore()
    
    # List of test jobs with varied roles and descriptions
    jobs = [
        {
            "title": "Senior Software Engineer",
            "description": "Looking for an experienced software engineer with 5+ years in Python, JavaScript, and cloud technologies. Must have strong experience with microservices architecture, CI/CD pipelines, and agile methodologies. Knowledge of AWS or Azure required.",
            "metadata": {"company": "TechCorp", "location": "Remote", "experience": "5+ years"}
        },
        {
            "title": "Data Scientist",
            "description": "Seeking a data scientist with expertise in machine learning, statistical analysis, and data visualization. Experience with Python, R, TensorFlow, and SQL required. Background in NLP preferred.",
            "metadata": {"company": "DataTech", "location": "New York", "experience": "3-5 years"}
        },
        {
            "title": "Frontend Developer",
            "description": "Frontend developer needed with strong React.js experience. Must be proficient in HTML5, CSS3, and modern JavaScript. Experience with TypeScript and state management libraries like Redux preferred.",
            "metadata": {"company": "WebSolutions", "location": "San Francisco", "experience": "2-4 years"}
        },
        {
            "title": "DevOps Engineer",
            "description": "Looking for a DevOps engineer with strong experience in Docker, Kubernetes, and infrastructure as code. Must be familiar with AWS services and automation tools like Terraform and Ansible.",
            "metadata": {"company": "CloudOps", "location": "Seattle", "experience": "4+ years"}
        },
        {
            "title": "Product Manager",
            "description": "Experienced product manager needed to lead product development initiatives. Strong understanding of agile methodologies, user research, and product lifecycle management required.",
            "metadata": {"company": "ProductCo", "location": "Boston", "experience": "5+ years"}
        },
        {
            "title": "UI/UX Designer",
            "description": "Creative UI/UX designer needed with expertise in user-centered design principles. Proficiency in Figma, Adobe Creative Suite, and prototyping tools required. Experience with design systems preferred.",
            "metadata": {"company": "DesignStudio", "location": "Los Angeles", "experience": "3+ years"}
        },
        {
            "title": "Backend Engineer",
            "description": "Backend engineer needed with strong Java/Spring Boot experience. Must be proficient in RESTful APIs, microservices, and database design. Knowledge of message queues and caching systems required.",
            "metadata": {"company": "ServerTech", "location": "Chicago", "experience": "4+ years"}
        },
        {
            "title": "Machine Learning Engineer",
            "description": "Seeking ML engineer with strong background in deep learning and computer vision. Experience with PyTorch, TensorFlow, and deployment of ML models to production required.",
            "metadata": {"company": "AILabs", "location": "Austin", "experience": "3+ years"}
        },
        {
            "title": "Cloud Solutions Architect",
            "description": "Cloud architect needed with extensive experience in AWS architecture. Must be familiar with serverless computing, microservices, and cloud security best practices.",
            "metadata": {"company": "CloudTech", "location": "Denver", "experience": "6+ years"}
        },
        {
            "title": "Mobile App Developer",
            "description": "Mobile developer needed with experience in both iOS (Swift) and Android (Kotlin) development. Knowledge of mobile architecture patterns and cross-platform frameworks like React Native preferred.",
            "metadata": {"company": "MobileApps", "location": "Miami", "experience": "3+ years"}
        },
        {
            "title": "Data Engineer",
            "description": "Data engineer needed with strong SQL and Python skills. Experience with data warehousing, ETL processes, and big data technologies like Spark required. Knowledge of cloud data services preferred.",
            "metadata": {"company": "DataFlow", "location": "Portland", "experience": "4+ years"}
        },
        {
            "title": "Security Engineer",
            "description": "Security engineer needed with experience in application security and penetration testing. Knowledge of security tools, OWASP guidelines, and compliance frameworks required.",
            "metadata": {"company": "SecureNet", "location": "Washington DC", "experience": "5+ years"}
        },
        {
            "title": "QA Automation Engineer",
            "description": "QA engineer needed with strong experience in automated testing frameworks. Proficiency in Selenium, TestNG, and CI/CD integration required. Experience with performance testing tools preferred.",
            "metadata": {"company": "QualityTech", "location": "Atlanta", "experience": "3+ years"}
        },
        {
            "title": "Blockchain Developer",
            "description": "Blockchain developer needed with experience in Ethereum and smart contract development. Knowledge of Solidity, Web3.js, and DApp architecture required.",
            "metadata": {"company": "BlockTech", "location": "San Diego", "experience": "2+ years"}
        },
        {
            "title": "Technical Project Manager",
            "description": "Technical PM needed with software development background. Must have experience managing complex technical projects, agile methodologies, and cross-functional teams.",
            "metadata": {"company": "ProjectPro", "location": "Philadelphia", "experience": "5+ years"}
        }
    ]
    
    # Store each job
    for job in jobs:
        try:
            store.store_job(
                job_title=job["title"],
                job_description=job["description"],
                job_metadata=job["metadata"]
            )
            print(f"Successfully added job: {job['title']}")
        except Exception as e:
            print(f"Error adding job {job['title']}: {str(e)}")

if __name__ == "__main__":
    add_test_jobs()