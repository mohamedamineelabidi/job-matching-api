import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

cur.execute("SELECT title, metadata->>'company', metadata->>'location' FROM job_embeddings")
jobs = cur.fetchall()

for job in jobs:
    print(f"Title: {job[0]}, Company: {job[1]}, Location: {job[2]}")

cur.close()
conn.close()