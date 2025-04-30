import os
import tempfile
from fastapi import UploadFile
from typing import Optional
import pymupdf4llm
from openai import AzureOpenAI

class CVProcessingService:
    def __init__(self):
        self.azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        self.gpt4_deployment_name = os.getenv("AZURE_OPENAI_GPT4_DEPLOYMENT")

        if not all([self.azure_api_key, self.azure_endpoint, self.api_version, self.gpt4_deployment_name]):
            raise ValueError("Missing required Azure OpenAI environment variables (API Key, Endpoint, API Version, GPT4 Deployment)")

        self.openai_client = AzureOpenAI(
            api_key=self.azure_api_key,
            api_version=self.api_version,
            azure_endpoint=self.azure_endpoint
            # Note: azure_deployment is often specified per-call, not globally here
        )
        self.cv_prompt = """
        You are a highly intelligent assistant tasked with analyzing CVs and creating concise, structured summaries optimized for comparing with job descriptions.

        Your goal is to extract and organize key details into specific categories. Structure your response as follows:

        1. **Professional Summary**: Provide a Five-sentences max overview of the candidate's career focus, expertise, and achievements.
        2. **Key Skills and Expertise**: Enumerate the candidate's main skills, including technical skills (e.g., programming languages, tools,frameworks, services) and non-technical skills (e.g., leadership, communication).
        3. **Work Experience**:
           - For each role, include:
             - Job Title.
             - Organization Name.
             - Duration of Employment.
             - Key responsibilities and accomplishments.
        4. **Technologies and Tools**: List every software, programming languages, frameworks,API service, and tools the candidate has experience with.
        5. **Education**: Summarize degrees, fields of study, and institutions attended.
        6. **Certifications and Training**: Highlight any certifications, courses, or training programs completed.
        7. **Languages**: Mention languages the candidate knows and their proficiency levels.
        8. **Projects**: Include significant projects or achievements relevant to the candidate's profile.
        9. **Keywords**: Extract important keywords that characterize the candidate's expertise.

        Focus on clarity and precision in each section to ensure a well-structured summary. Here's the CV content:

        {content}

        Respond in the requested structured format.
        """

    async def process_cv(self, cv_file: UploadFile) -> str:
        """Process CV file and return structured content"""
        try:
            # Read file content
            content = await cv_file.read()
            
            # If file is markdown, use content directly
            if cv_file.filename.endswith('.md'):
                cv_text = content.decode('utf-8')
            else:
                # For other file types (e.g. PDF), use temporary file and PyMuPDF
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(cv_file.filename)[1]) as temp_file:
                    temp_file.write(content)
                    temp_path = temp_file.name

                # Extract text using PyMuPDF
                cv_markdown = pymupdf4llm.to_markdown(temp_path, page_chunks=True)
                cv_text = " ".join([chunk['text'] for chunk in cv_markdown])
                
                # Clean up temporary file
                os.remove(temp_path)

            # Generate structured summary using OpenAI
            response = self.openai_client.chat.completions.create(
                model=self.gpt4_deployment_name, # Use the deployment name from env
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": self.cv_prompt.format(content=cv_text)}
                ],
                temperature=0,
                max_tokens=2048
            )

            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"Error processing CV: {str(e)}")
