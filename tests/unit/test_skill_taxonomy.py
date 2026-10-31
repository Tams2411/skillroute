"""Unit tests for skill taxonomy."""

from career_coach.domain.skill_taxonomy import SkillTaxonomy, load_taxonomy, DEFAULT_TAXONOMY


class TestSkillTaxonomy:
    """Test skill taxonomy loading and lookup."""

    def test_load_taxonomy(self):
        taxonomy = load_taxonomy()
        assert isinstance(taxonomy, SkillTaxonomy)
        assert len(taxonomy.skills) > 0

    def test_canonical_lookup(self):
        taxonomy = load_taxonomy()

        # Test exact canonical match
        canonical = taxonomy.get_canonical("python")
        assert canonical == "python"

        canonical = taxonomy.get_canonical("sql")
        assert canonical == "sql"

    def test_alias_lookup(self):
        taxonomy = load_taxonomy()

        # Test alias matching
        canonical = taxonomy.get_canonical("py")
        assert canonical is None

        canonical = taxonomy.get_canonical("postgresql")
        assert canonical == "postgresql"

        canonical = taxonomy.get_canonical("k8s")
        assert canonical == "kubernetes"

    def test_case_insensitive_lookup(self):
        taxonomy = load_taxonomy()

        canonical = taxonomy.get_canonical("PYTHON")
        assert canonical == "python"

        canonical = taxonomy.get_canonical("Python")
        assert canonical == "python"

        canonical = taxonomy.get_canonical("PyThOn")
        assert canonical == "python"

    def test_unknown_skill_returns_none(self):
        taxonomy = load_taxonomy()

        canonical = taxonomy.get_canonical("nonexistent_skill_xyz")
        assert canonical is None

    def test_get_category(self):
        taxonomy = load_taxonomy()

        category = taxonomy.get_category("python")
        assert category == "programming"

        category = taxonomy.get_category("sql")
        assert category == "data"

        category = taxonomy.get_category("docker")
        assert category == "devops"

    def test_all_canonical(self):
        taxonomy = load_taxonomy()

        canonical_skills = taxonomy.all_canonical()
        assert isinstance(canonical_skills, list)
        assert len(canonical_skills) > 20
        assert "python" in canonical_skills
        assert "sql" in canonical_skills

    def test_all_aliases(self):
        taxonomy = load_taxonomy()

        aliases = taxonomy.all_aliases()
        assert isinstance(aliases, list)
        assert len(aliases) > len(taxonomy.skills)  # More aliases than canonical skills

        # Check structure: (alias_lower, canonical)
        for alias, canonical in aliases:
            assert isinstance(alias, str)
            assert isinstance(canonical, str)
            assert alias == alias.lower()

    def test_default_taxonomy_completeness(self):
        """Verify default taxonomy has expected skills."""
        expected_skills = [
            "python",
            "sql",
            "pandas",
            "numpy",
            "pytorch",
            "tensorflow",
            "airflow",
            "docker",
            "kubernetes",
            "aws",
            "spark",
            "kafka",
            "fastapi",
            "react",
            "typescript",
            "git",
            "terraform",
            "mlflow",
            "kubeflow",
            "redshift",
            "dbt",
            "great expectations",
        ]

        for skill in expected_skills:
            assert skill in DEFAULT_TAXONOMY.skills, f"Missing expected skill: {skill}"

    def test_singleton_behavior(self):
        """Test that load_taxonomy returns the same instance."""
        t1 = load_taxonomy()
        t2 = load_taxonomy()
        assert t1 is t2
