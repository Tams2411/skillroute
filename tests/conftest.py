"""Test configuration and fixtures."""

import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture
def sample_resume_text():
    """Sample resume text for testing."""
    return """Alex Chen
Data Engineer | alex.chen@email.com

SUMMARY
Data Engineer with 3 years building scalable data pipelines.

TECHNICAL SKILLS
- Languages: Python, SQL, Bash
- Data: Pandas, NumPy, PySpark, PostgreSQL, MySQL
- Orchestration: Apache Airflow (2 years), dbt
- Cloud: AWS (S3, EC2, RDS, Lambda), Docker
- CI/CD: GitHub Actions, GitLab CI

EXPERIENCE
Data Engineer | TechCorp Inc. | 2022-Present
- Built and maintain 50+ Airflow DAGs processing 10TB+ daily
- Migrated legacy ETL to PySpark, reducing runtime by 60%
- Implemented data quality checks with Great Expectations
- Designed star schema for analytics warehouse (PostgreSQL)
- Containerized pipelines with Docker, deployed on ECS

EDUCATION
BS Computer Science | State University | 2021"""


@pytest.fixture
def sample_jd_text():
    """Sample job description for testing."""
    return """Senior Data Engineer

Required Skills:
- 5+ years of experience with Python
- Expert level SQL and database design (PostgreSQL, MySQL)
- Strong experience with Apache Airflow for orchestration
- Hands-on experience with Apache Spark and PySpark
- Experience with AWS (S3, Redshift, Lambda, Glue)
- Docker and Kubernetes for container orchestration
- CI/CD pipelines (GitHub Actions, GitLab CI)
- Data modeling and schema design

Preferred Skills:
- Experience with Kafka for event streaming
- Terraform for infrastructure as code
- Machine learning pipeline experience (MLflow, Kubeflow)

Responsibilities:
- Design and build scalable data pipelines
- Optimize query performance and data storage costs"""


@pytest.fixture
def temp_pdf_file():
    """Create a temporary PDF file for testing."""
    import pypdf
    from io import BytesIO
    
    # Create a simple PDF in memory
    writer = pypdf.PdfWriter()
    page = pypdf.PageObject.create_blank_page(width=612, height=792)
    # Note: Can't easily add text to blank page without more work
    # This fixture provides a path that tests can use
    
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        writer.add_page(page)
        writer.write(f)
        temp_path = f.name
    
    yield temp_path
    
    try:
        os.unlink(temp_path)
    except Exception:
        pass


@pytest.fixture
def temp_txt_file(sample_resume_text):
    """Create a temporary text file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(sample_resume_text)
        temp_path = f.name
    
    yield temp_path
    
    try:
        os.unlink(temp_path)
    except Exception:
        pass