"""Curated skill taxonomy for normalization."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
import json
from pathlib import Path


class SkillEntry(BaseModel):
    """A single skill entry in the taxonomy."""
    model_config = ConfigDict(extra="forbid")

    canonical: str = Field(min_length=1, max_length=80)
    aliases: list[str] = Field(default_factory=list)
    category: str = Field(min_length=1, max_length=50)
    related: list[str] = Field(default_factory=list)


class SkillTaxonomy(BaseModel):
    """Complete skill taxonomy."""
    model_config = ConfigDict(extra="forbid")

    skills: dict[str, SkillEntry] = Field(default_factory=dict)

    def get_canonical(self, term: str) -> Optional[str]:
        """Map a term to its canonical skill name."""
        normalized = term.lower().strip()
        for canonical, entry in self.skills.items():
            if canonical.lower() == normalized:
                return canonical
            for alias in entry.aliases:
                if alias.lower() == normalized:
                    return canonical
        return None

    def get_category(self, canonical: str) -> Optional[str]:
        """Get the category for a canonical skill."""
        entry = self.skills.get(canonical)
        return entry.category if entry else None

    def all_canonical(self) -> list[str]:
        """Get all canonical skill names."""
        return list(self.skills.keys())

    def all_aliases(self) -> list[tuple[str, str]]:
        """Get all (alias, canonical) pairs."""
        pairs = []
        for canonical, entry in self.skills.items():
            pairs.append((canonical.lower(), canonical))
            for alias in entry.aliases:
                pairs.append((alias.lower(), canonical))
        return pairs


# Default taxonomy for data/ML/engineering roles
DEFAULT_TAXONOMY = SkillTaxonomy(skills={
    "python": SkillEntry(canonical="python", aliases=["python", "python programming"], category="programming"),
    "sql": SkillEntry(canonical="sql", aliases=["sql", "structured query language"], category="data"),
    "mysql": SkillEntry(canonical="mysql", aliases=["mysql"], category="data"),
    "sqlite": SkillEntry(canonical="sqlite", aliases=["sqlite"], category="data"),
    "pandas": SkillEntry(canonical="pandas", aliases=["pandas", "pandas python"], category="data"),
    "numpy": SkillEntry(canonical="numpy", aliases=["numpy", "numpy python"], category="data"),
    "pytorch": SkillEntry(canonical="pytorch", aliases=["pytorch", "torch"], category="ml"),
    "tensorflow": SkillEntry(canonical="tensorflow", aliases=["tensorflow"], category="ml"),
    "keras": SkillEntry(canonical="keras", aliases=["keras"], category="ml"),
    "scikit-learn": SkillEntry(canonical="scikit-learn", aliases=["scikit-learn", "sklearn", "sklearn python"], category="ml"),
    "airflow": SkillEntry(canonical="airflow", aliases=["apache airflow", "airflow", "airflow orchestrator"], category="orchestration"),
    "docker": SkillEntry(canonical="docker", aliases=["docker", "containerization", "docker containers"], category="devops"),
    "kubernetes": SkillEntry(canonical="kubernetes", aliases=["kubernetes", "k8s", "k8s orchestration"], category="devops"),
    "aws": SkillEntry(canonical="aws", aliases=["aws", "amazon web services", "amazon aws"], category="cloud"),
    "gcp": SkillEntry(canonical="gcp", aliases=["gcp", "google cloud", "google cloud platform"], category="cloud"),
    "azure": SkillEntry(canonical="azure", aliases=["azure", "microsoft azure"], category="cloud"),
    "spark": SkillEntry(canonical="spark", aliases=["apache spark", "spark"], category="data engineering"),
    "pyspark": SkillEntry(canonical="pyspark", aliases=["pyspark", "apache pyspark"], category="data engineering"),
    "scala": SkillEntry(canonical="scala", aliases=["scala", "scala programming"], category="programming"),
    "kafka": SkillEntry(canonical="kafka", aliases=["apache kafka", "kafka", "kafka messaging"], category="data engineering"),
    "redis": SkillEntry(canonical="redis", aliases=["redis", "redis cache"], category="data engineering"),
    "postgresql": SkillEntry(canonical="postgresql", aliases=["postgresql", "postgres", "psql"], category="data"),
    "redshift": SkillEntry(canonical="redshift", aliases=["redshift", "amazon redshift"], category="cloud"),
    "mlflow": SkillEntry(canonical="mlflow", aliases=["mlflow"], category="ml"),
    "kubeflow": SkillEntry(canonical="kubeflow", aliases=["kubeflow"], category="ml"),
    "dbt": SkillEntry(canonical="dbt", aliases=["dbt", "data build tool"], category="data engineering"),
    "great expectations": SkillEntry(
        canonical="great expectations",
        aliases=["great expectations", "great expectations framework"],
        category="data",
    ),
    "mongodb": SkillEntry(canonical="mongodb", aliases=["mongodb", "mongo"], category="data"),
    "nosql": SkillEntry(canonical="nosql", aliases=["nosql", "no sql"], category="data"),
    "elasticsearch": SkillEntry(canonical="elasticsearch", aliases=["elasticsearch", "elastic search"], category="data engineering"),
    "fastapi": SkillEntry(canonical="fastapi", aliases=["fastapi", "fast api"], category="backend"),
    "flask": SkillEntry(canonical="flask", aliases=["flask", "flask python"], category="backend"),
    "django": SkillEntry(canonical="django", aliases=["django", "django python"], category="backend"),
    "react": SkillEntry(canonical="react", aliases=["react", "reactjs", "react.js"], category="frontend"),
    "typescript": SkillEntry(canonical="typescript", aliases=["typescript"], category="frontend"),
    "git": SkillEntry(canonical="git", aliases=["git"], category="tools"),
    "github": SkillEntry(canonical="github", aliases=["github"], category="tools"),
    "gitlab": SkillEntry(canonical="gitlab", aliases=["gitlab"], category="tools"),
    "version control": SkillEntry(canonical="version control", aliases=["version control", "source control"], category="tools"),
    "ci/cd": SkillEntry(canonical="ci/cd", aliases=["ci/cd", "continuous integration", "continuous deployment"], category="devops"),
    "github actions": SkillEntry(canonical="github actions", aliases=["github actions"], category="devops"),
    "gitlab ci": SkillEntry(canonical="gitlab ci", aliases=["gitlab ci"], category="devops"),
    "terraform": SkillEntry(canonical="terraform", aliases=["terraform", "infrastructure as code", "iac"], category="devops"),
    "mlops": SkillEntry(canonical="mlops", aliases=["mlops", "ml ops", "machine learning operations"], category="ml"),
    "feature engineering": SkillEntry(canonical="feature engineering", aliases=["feature engineering", "feature eng"], category="ml"),
    "model deployment": SkillEntry(canonical="model deployment", aliases=["model deployment", "model serving", "model serving api"], category="ml"),
    "data visualization": SkillEntry(canonical="data visualization", aliases=["data visualization", "visualization"], category="data"),
    "matplotlib": SkillEntry(canonical="matplotlib", aliases=["matplotlib"], category="data visualization"),
    "seaborn": SkillEntry(canonical="seaborn", aliases=["seaborn"], category="data visualization"),
    "plotly": SkillEntry(canonical="plotly", aliases=["plotly"], category="data visualization"),
    "tableau": SkillEntry(canonical="tableau", aliases=["tableau"], category="data visualization"),
    "power bi": SkillEntry(canonical="power bi", aliases=["power bi", "powerbi"], category="data visualization"),
    "statistics": SkillEntry(canonical="statistics", aliases=["statistics", "statistical analysis"], category="data"),
    "probability": SkillEntry(canonical="probability", aliases=["probability", "probabilistic modeling"], category="data"),
    "algorithms": SkillEntry(canonical="algorithms", aliases=["algorithms", "algo", "data structures and algorithms", "dsa"], category="programming"),
    "system design": SkillEntry(canonical="system design", aliases=["system design", "architecture design"], category="backend"),
    "distributed systems": SkillEntry(canonical="distributed systems", aliases=["distributed systems"], category="backend"),
    "microservices": SkillEntry(canonical="microservices", aliases=["microservices", "micro services", "service oriented architecture"], category="backend"),
    "rest api": SkillEntry(canonical="rest api", aliases=["rest api", "restful api"], category="backend"),
    "graphql": SkillEntry(canonical="graphql", aliases=["graphql", "graph ql"], category="backend"),
    "testing": SkillEntry(canonical="testing", aliases=["testing", "unit testing", "integration testing"], category="programming"),
    "pytest": SkillEntry(canonical="pytest", aliases=["pytest"], category="programming"),
    "jest": SkillEntry(canonical="jest", aliases=["jest"], category="programming"),
    "agile": SkillEntry(canonical="agile", aliases=["agile", "agile methodology"], category="process"),
    "scrum": SkillEntry(canonical="scrum", aliases=["scrum"], category="process"),
    "kanban": SkillEntry(canonical="kanban", aliases=["kanban"], category="process"),
})


def load_taxonomy(path: Optional[Path] = None) -> SkillTaxonomy:
    """Load taxonomy from JSON file or return default."""
    if path and path.exists():
        with open(path) as f:
            data = json.load(f)
        skills = {k: SkillEntry(**v) for k, v in data.get("skills", {}).items()}
        return SkillTaxonomy(skills=skills)
    return DEFAULT_TAXONOMY


def save_taxonomy(taxonomy: SkillTaxonomy, path: Path) -> None:
    """Save taxonomy to JSON file."""
    data = {"skills": {k: v.model_dump() for k, v in taxonomy.skills.items()}}
    with open(path, "w") as f:
        json.dump(data, f, indent=2)