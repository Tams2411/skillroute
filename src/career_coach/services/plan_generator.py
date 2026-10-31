"""Learning plan generation service."""

from career_coach.domain.schemas import (
    LearningTask, ProjectRecommendation, SkillGap
)
from career_coach.domain.scoring import get_top_gaps
from career_coach.domain.skill_taxonomy import load_taxonomy
from typing import Optional


# Learning resource templates by skill category
LEARNING_RESOURCES = {
    "programming": [
        {"title": "Official Python Tutorial", "url": "https://docs.python.org/3/tutorial/", "type": "doc", "hours": 8},
        {"title": "Effective Python (Book)", "url": "https://effectivepython.com/", "type": "book", "hours": 20},
        {"title": "Real Python Articles", "url": "https://realpython.com/", "type": "article", "hours": 10},
    ],
    "data": [
        {"title": "SQL for Data Analysis (Mode)", "url": "https://mode.com/sql-tutorial/", "type": "course", "hours": 12},
        {"title": "Pandas Documentation", "url": "https://pandas.pydata.org/docs/", "type": "doc", "hours": 8},
        {"title": "Data Analysis with Python (freeCodeCamp)", "url": "https://www.freecodecamp.org/learn/data-analysis-with-python/", "type": "course", "hours": 20},
    ],
    "ml": [
        {"title": "Hands-On ML with Scikit-Learn & TF (Book)", "url": "https://github.com/ageron/handson-ml2", "type": "book", "hours": 40},
        {"title": "Fast.ai Practical Deep Learning", "url": "https://course.fast.ai/", "type": "course", "hours": 60},
        {"title": "MLOps Zoomcamp", "url": "https://github.com/DataTalksClub/mlops-zoomcamp", "type": "course", "hours": 30},
    ],
    "cloud": [
        {"title": "AWS Cloud Practitioner Essentials", "url": "https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/", "type": "course", "hours": 8},
        {"title": "Google Cloud Fundamentals", "url": "https://www.cloudskillsboost.google/course_templates/626", "type": "course", "hours": 10},
    ],
    "devops": [
        {"title": "Docker Mastery (Udemy)", "url": "https://www.udemy.com/course/docker-mastery/", "type": "course", "hours": 15},
        {"title": "Kubernetes the Hard Way", "url": "https://github.com/kelseyhightower/kubernetes-the-hard-way", "type": "project", "hours": 40},
        {"title": "Terraform Up & Running (Book)", "url": "https://www.terraformupandrunning.com/", "type": "book", "hours": 20},
    ],
    "orchestration": [
        {"title": "Apache Airflow Documentation", "url": "https://airflow.apache.org/docs/", "type": "doc", "hours": 10},
        {"title": "Astronomer Airflow Tutorial", "url": "https://www.astronomer.io/guides/", "type": "article", "hours": 8},
    ],
    "backend": [
        {"title": "FastAPI Documentation", "url": "https://fastapi.tiangolo.com/", "type": "doc", "hours": 6},
        {"title": "Designing Data-Intensive Applications (Book)", "url": "https://dataintensiveapplications.com/", "type": "book", "hours": 30},
    ],
    "frontend": [
        {"title": "React Official Tutorial", "url": "https://react.dev/learn", "type": "doc", "hours": 8},
        {"title": "TypeScript Handbook", "url": "https://www.typescriptlang.org/docs/", "type": "doc", "hours": 6},
    ],
    "tools": [
        {"title": "Git Pro Book", "url": "https://git-scm.com/book/en/v2", "type": "book", "hours": 10},
    ],
    "process": [
        {"title": "Agile Manifesto & Principles", "url": "https://agilemanifesto.org/", "type": "article", "hours": 2},
    ],
    "data engineering": [
        {"title": "Data Engineering Zoomcamp", "url": "https://github.com/DataTalksClub/data-engineering-zoomcamp", "type": "course", "hours": 60},
        {"title": "Designing Data-Intensive Applications (Book)", "url": "https://dataintensiveapplications.com/", "type": "book", "hours": 30},
    ],
}


# Project templates by skill
PROJECT_TEMPLATES = {
    "python": {
        "title": "CLI Tool with Click/Typer",
        "description": "Build a useful command-line tool with proper packaging, tests, and CI",
        "skills": ["python", "testing", "ci/cd"],
        "deliverables": ["PyPI package", "GitHub Actions CI", "README with demo"],
        "acceptance": "Tool installs via pip, passes tests, has --help documentation",
    },
    "sql": {
        "title": "Analytics Dashboard with dbt",
        "description": "Model a dataset with dbt, create incremental models, add tests and documentation",
        "skills": ["sql", "postgresql", "data visualization"],
        "deliverables": ["dbt project", "ERD diagram", "Dashboard screenshots"],
        "acceptance": "dbt run succeeds, all tests pass, docs generate",
    },
    "airflow": {
        "title": "Data Pipeline Orchestration",
        "description": "Build an Airflow DAG with sensors, branching, and dynamic task mapping",
        "skills": ["airflow", "python", "docker"],
        "deliverables": ["DAG code", "Docker Compose for local Airflow", "Task dependency diagram"],
        "acceptance": "DAG runs end-to-end locally, handles retries, has SLA alerts",
    },
    "docker": {
        "title": "Multi-stage Docker Build",
        "description": "Create optimized multi-stage Dockerfile for a Python/Node app with security scanning",
        "skills": ["docker", "ci/cd", "security"],
        "deliverables": ["Dockerfile", "docker-compose.yml", "Trivy scan report"],
        "acceptance": "Image <200MB, passes Trivy scan, builds in CI",
    },
    "kubernetes": {
        "title": "K8s Deployment with Helm",
        "description": "Deploy a microservice to local k8s (kind/k3d) with Helm chart, ingress, and HPA",
        "skills": ["kubernetes", "helm", "docker"],
        "deliverables": ["Helm chart", "values.yaml for dev/staging/prod", "Load test results"],
        "acceptance": "Service accessible via ingress, HPA scales under load",
    },
    "aws": {
        "title": "Serverless Data Pipeline",
        "description": "Build S3 -> Lambda -> DynamoDB pipeline with SAM/CDK and CloudWatch monitoring",
        "skills": ["aws", "python", "ci/cd"],
        "deliverables": ["SAM/CDK template", "Lambda code", "CloudWatch dashboard"],
        "acceptance": "Pipeline processes test files, metrics visible in CloudWatch",
    },
    "spark": {
        "title": "Spark ETL Job",
        "description": "Write a PySpark job that reads from S3, transforms, and writes to Delta Lake",
        "skills": ["spark", "python", "aws"],
        "deliverables": ["PySpark script", "Databricks/EMR config", "Performance benchmarks"],
        "acceptance": "Job completes on 1GB+ dataset, handles skew, outputs valid Delta",
    },
    "kafka": {
        "title": "Event-Driven Service",
        "description": "Build a producer/consumer pair with schema registry and exactly-once semantics",
        "skills": ["kafka", "python", "docker"],
        "deliverables": ["Producer code", "Consumer code", "Schema registry setup"],
        "acceptance": "Messages round-trip with schema validation, no duplicates",
    },
    "fastapi": {
        "title": "REST API with Auth",
        "description": "Build a FastAPI service with JWT auth, PostgreSQL, and OpenAPI docs",
        "skills": ["fastapi", "postgresql", "testing"],
        "deliverables": ["API code", "Postman collection", "Deploy to Render/Fly.io"],
        "acceptance": "All endpoints documented, auth works, 90%+ test coverage",
    },
    "react": {
        "title": "Dashboard with React + TypeScript",
        "description": "Build a data dashboard with charts, filtering, and responsive layout",
        "skills": ["react", "typescript", "data visualization"],
        "deliverables": ["Vite/Next.js app", "Storybook components", "Deploy to Vercel"],
        "acceptance": "Dashboard loads <2s, works on mobile, charts interactive",
    },
    "terraform": {
        "title": "Infrastructure Module",
        "description": "Write a reusable Terraform module for VPC/RDS/ECS with tests",
        "skills": ["terraform", "aws", "ci/cd"],
        "deliverables": ["Module code", "Terratest tests", "Example usage"],
        "acceptance": "terraform plan/apply succeeds, tests pass in CI",
    },
    "mlops": {
        "title": "ML Model Deployment",
        "description": "Train a model, version with MLflow, deploy with FastAPI + Docker, add monitoring",
        "skills": ["mlops", "mlflow", "fastapi", "docker"],
        "deliverables": ["Training pipeline", "MLflow tracking", "Serving API", "Drift detection"],
        "acceptance": "Model serves predictions, metrics logged, drift alerts work",
    },
}

SKILL_LEARNING_RESOURCES = {
    "docker": [
        {"title": "Docker Get Started", "url": "https://docs.docker.com/get-started/", "type": "doc", "hours": 4},
        {"title": "Docker Guides", "url": "https://docs.docker.com/guides/", "type": "doc", "hours": 6},
        {"title": "Docker Build Tutorials", "url": "https://docs.docker.com/build/building/", "type": "tutorial", "hours": 5},
    ],
    "kubernetes": [
        {"title": "Kubernetes Basics", "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/", "type": "tutorial", "hours": 6},
        {"title": "Kubernetes Concepts", "url": "https://kubernetes.io/docs/concepts/", "type": "doc", "hours": 8},
        {"title": "Kubernetes Tasks", "url": "https://kubernetes.io/docs/tasks/", "type": "doc", "hours": 8},
    ],
    "terraform": [
        {"title": "Terraform Tutorials", "url": "https://developer.hashicorp.com/terraform/tutorials", "type": "tutorial", "hours": 8},
        {"title": "Terraform Language Documentation", "url": "https://developer.hashicorp.com/terraform/language", "type": "doc", "hours": 8},
        {"title": "Terraform Associate Study Guide", "url": "https://developer.hashicorp.com/terraform/tutorials/certification-003", "type": "guide", "hours": 6},
    ],
    "redshift": [
        {"title": "Amazon Redshift Getting Started", "url": "https://docs.aws.amazon.com/redshift/latest/gsg/getting-started.html", "type": "doc", "hours": 6},
        {"title": "Redshift Database Developer Guide", "url": "https://docs.aws.amazon.com/redshift/latest/dg/welcome.html", "type": "doc", "hours": 8},
    ],
    "dbt": [
        {"title": "dbt Documentation", "url": "https://docs.getdbt.com/docs/introduction", "type": "doc", "hours": 6},
        {"title": "dbt Learn", "url": "https://learn.getdbt.com/", "type": "course", "hours": 10},
    ],
    "great expectations": [
        {"title": "Great Expectations Documentation", "url": "https://docs.greatexpectations.io/docs/", "type": "doc", "hours": 6},
    ],
    "mlflow": [
        {"title": "MLflow Documentation", "url": "https://mlflow.org/docs/latest/index.html", "type": "doc", "hours": 6},
        {"title": "MLflow Tracking Quickstart", "url": "https://mlflow.org/docs/latest/ml/tracking/quickstart/", "type": "tutorial", "hours": 4},
    ],
    "kubeflow": [
        {"title": "Kubeflow Documentation", "url": "https://www.kubeflow.org/docs/", "type": "doc", "hours": 8},
        {"title": "Kubeflow Pipelines Tutorials", "url": "https://www.kubeflow.org/docs/components/pipelines/getting-started/", "type": "tutorial", "hours": 8},
    ],
}


def get_resources_for_skill(skill: str, max_resources: int = 3) -> list[dict]:
    """Get learning resources for a skill based on its category."""
    specific_resources = SKILL_LEARNING_RESOURCES.get(skill.lower())
    if specific_resources:
        return [dict(resource) for resource in specific_resources[:max_resources]]

    taxonomy = load_taxonomy()
    category = taxonomy.get_category(skill)
    
    if category and category in LEARNING_RESOURCES:
        resources = LEARNING_RESOURCES[category][:max_resources]
    else:
        resources = [
            {"title": f"{skill.title()} Official Documentation", "url": "", "type": "doc", "hours": 5},
            {"title": f"Learn {skill.title()} (freeCodeCamp/YouTube)", "url": "", "type": "course", "hours": 10},
        ]
    
    return resources


def get_project_for_skill(skill: str) -> Optional[dict]:
    """Get a project template for a skill."""
    taxonomy = load_taxonomy()
    
    if skill in PROJECT_TEMPLATES:
        return PROJECT_TEMPLATES[skill]
    
    category = taxonomy.get_category(skill)
    category_projects = {
        "programming": "python",
        "data": "sql",
        "ml": "mlops",
        "cloud": "aws",
        "devops": "docker",
        "orchestration": "airflow",
        "backend": "fastapi",
        "frontend": "react",
        "data engineering": "spark",
    }
    
    if category and category in category_projects:
        return PROJECT_TEMPLATES.get(category_projects[category])
    
    return None


def generate_learning_plan(
    gaps: list[SkillGap],
    weeks: int = 8,
    hours_per_week: int = 15,
) -> list[LearningTask]:
    """
    Generate a weekly learning plan from skill gaps.
    Matches the LearningTask schema: week, skill, focus, learning_task, practice_task, deliverable, acceptance_criteria, estimated_hours
    """
    if not gaps:
        return []
    
    actionable = [g for g in gaps if g.priority >= 0.15]
    top_gaps = get_top_gaps(actionable, n=min(len(actionable), weeks * 2))
    
    if not top_gaps:
        return []
    
    tasks = []
    week = 1
    
    for i, gap in enumerate(top_gaps):
        if week > weeks:
            break
        
        skill = gap.canonical_skill
        resources = get_resources_for_skill(skill)
        total_resource_hours = sum(r["hours"] for r in resources)
        
        skill_weeks = max(1, min(2, (total_resource_hours + hours_per_week - 1) // hours_per_week))
        
        for w in range(skill_weeks):
            if week > weeks:
                break
            
            week_resources = resources[w::skill_weeks] if skill_weeks > 1 else resources
            week_hours = sum(r["hours"] for r in week_resources) or hours_per_week
            week_hours = min(week_hours, hours_per_week)
            
            resource_names = ", ".join([r['title'] for r in week_resources]) if week_resources else "Core concepts"
            
            learning_task = f"Study {resource_names}. Focus on core concepts, syntax, and common patterns for {skill}."
            practice_task = f"Complete hands-on exercises for {skill}. Build a small demo showcasing key features."
            
            task = LearningTask(
                week=week,
                skill=skill,
                focus=f"Master {skill} fundamentals and practical application",
                learning_task=learning_task,
                practice_task=practice_task,
                deliverable=f"Notes + working code examples for {skill}",
                acceptance_criteria=f"Can explain {skill} concepts; complete practice exercises; document key learnings",
                estimated_hours=week_hours,
                dependencies=[],
                completed=False,
            )
            tasks.append(task)
            week += 1
    
    while week <= weeks:
        if tasks:
            skill = tasks[-1].skill
            task = LearningTask(
                week=week,
                skill=skill,
                focus=f"Apply {skill} in a portfolio project",
                learning_task=f"Design and plan a small project using {skill}. Review advanced patterns.",
                practice_task="Build the project end-to-end. Write tests, documentation, and deploy if applicable.",
                deliverable=f"GitHub repo with {skill} portfolio project",
                acceptance_criteria=f"Project demonstrates {skill} proficiency; code is clean; README explains usage",
                estimated_hours=hours_per_week,
                dependencies=[f"Week {week-1} {skill} learning"],
                completed=False,
            )
            tasks.append(task)
        week += 1
    
    return tasks


def generate_project_recommendations(
    gaps: list[SkillGap],
    max_projects: int = 3,
) -> list[ProjectRecommendation]:
    """Generate portfolio project recommendations from top gaps.
    
    Matches ProjectRecommendation schema: title, targeted_skills, reasoning, scope, deliverables, acceptance_criteria, estimated_hours, difficulty, limitations, stretch_goals
    """
    if max_projects <= 0:
        return []

    actionable = [g for g in gaps if g.priority >= 0.15]
    top_gaps = get_top_gaps(actionable, n=len(actionable))

    recommendations = []
    recommendations_by_title: dict[str, ProjectRecommendation] = {}

    for gap in top_gaps:
        skill = gap.canonical_skill
        template = get_project_for_skill(skill)
        project_title = template["title"] if template else f"{skill.title()} Portfolio Project"
        existing = recommendations_by_title.get(project_title)
        if existing:
            existing.targeted_skills = list(dict.fromkeys([*existing.targeted_skills, skill]))
            existing.reasoning = (
                f"{existing.reasoning} Also addresses the {skill} skill gap."
            )[:1000]
            continue

        if template:
            recommendation = ProjectRecommendation(
                title=project_title,
                targeted_skills=list(dict.fromkeys([*template["skills"], skill])),
                reasoning=f"Addresses top skill gap: {skill} (priority: {gap.priority:.0%}). {gap.reason}",
                scope=template["description"],
                deliverables=template["deliverables"],
                acceptance_criteria=[template["acceptance"]],
                estimated_hours=40.0,
                difficulty="intermediate",
                limitations="Requires dedicated time; may need cloud credits for deployment",
                stretch_goals=["Add CI/CD pipeline", "Write technical blog post", "Present at meetup"],
            )
        else:
            recommendation = ProjectRecommendation(
                title=project_title,
                targeted_skills=[skill],
                reasoning=f"Addresses skill gap: {skill} (priority: {gap.priority:.0%})",
                scope=f"Build a project demonstrating {skill} proficiency with real-world scope",
                deliverables=["Working code", "README", "Demo/video"],
                acceptance_criteria=[f"Project uses {skill} meaningfully", "Code is clean and documented"],
                estimated_hours=30.0,
                difficulty="intermediate",
                limitations="Scope may need adjustment based on available time",
                stretch_goals=["Add tests", "Deploy to cloud", "Add monitoring"],
            )

        recommendations_by_title[project_title] = recommendation
        recommendations.append(recommendation)
        if len(recommendations) >= max_projects:
            break
    
    return recommendations