from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from .config import GLOBAL_RANDOM_SEED


@dataclass
class Employee:
    employee_id: str
    business_unit: str
    region: str
    job_family: str
    current_role: str
    tenure_months: int
    skills: List[str]


@dataclass
class CatalogItem:
    item_id: str
    title: str
    description: str
    skills_required: List[str]
    category: str
    role_family: str
    is_mandatory: bool
    is_strategic: bool
    item_type: str  # learning/project/role


@dataclass
class SyntheticWorld:
    employees: List[Employee] = field(default_factory=list)
    items: List[CatalogItem] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)


BUSINESS_UNITS = ["BU_A", "BU_B", "BU_C"]
REGIONS = ["NA", "EMEA", "APAC"]
JOB_FAMILIES = ["Engineering", "Sales", "HR", "Operations"]
CATEGORIES = ["Foundational", "Advanced", "Leadership", "Compliance"]


def generate_skill_ids(n: int) -> List[str]:
    return [f"skill_{i:03d}" for i in range(n)]


def create_synthetic_world(n_employees: int, n_items: int, item_type: str) -> SyntheticWorld:
    rng = random.Random(GLOBAL_RANDOM_SEED + hash(item_type) % 1000 + n_employees + n_items)

    n_skills = 60
    skills = generate_skill_ids(n_skills)

    employees: List[Employee] = []
    for i in range(n_employees):
        bu = rng.choice(BUSINESS_UNITS)
        region = rng.choice(REGIONS)
        job_family = rng.choice(JOB_FAMILIES)
        role = f"{job_family}_L{rng.randint(1, 4)}"
        tenure = rng.randint(6, 120)
        # employees have 5–10 skills
        n_emp_skills = rng.randint(5, 10)
        emp_skills = rng.sample(skills, n_emp_skills)
        employees.append(
            Employee(
                employee_id=f"emp_{i:04d}",
                business_unit=bu,
                region=region,
                job_family=job_family,
                current_role=role,
                tenure_months=tenure,
                skills=emp_skills,
            )
        )

    items: List[CatalogItem] = []
    for j in range(n_items):
        role_family = rng.choice(JOB_FAMILIES)
        category = rng.choice(CATEGORIES)
        n_item_skills = rng.randint(3, 8)
        skills_required = rng.sample(skills, n_item_skills)
        is_mandatory = (category == "Compliance") and (rng.random() < 0.3)
        is_strategic = (category != "Compliance") and (rng.random() < 0.2)
        title = f"{item_type.title()} Item {j}"
        description = f"A {category.lower()} {item_type} focused on key skills."
        items.append(
            CatalogItem(
                item_id=f"{item_type}_{j:04d}",
                title=title,
                description=description,
                skills_required=skills_required,
                category=category,
                role_family=role_family,
                is_mandatory=is_mandatory,
                is_strategic=is_strategic,
                item_type=item_type,
            )
        )

    return SyntheticWorld(employees=employees, items=items, skills=skills)


def compute_similarity_score(emp: Employee, item: CatalogItem) -> float:
    """Simple overlap-based skill similarity in [0,1].

    This is not used directly as the model score; it's a latent ground-truth
    for generating engagement probabilities.
    """

    s_emp = set(emp.skills)
    s_item = set(item.skills_required)
    if not s_emp or not s_item:
        return 0.0
    overlap = len(s_emp & s_item)
    denom = math.sqrt(len(s_emp) * len(s_item))
    if denom == 0:
        return 0.0
    return overlap / denom


def ground_truth_engagement_probability(emp: Employee, item: CatalogItem) -> float:
    """Return a probability in [0,1] representing latent engagement likelihood.

    This is used by the simulation to determine whether an employee engages
    with a recommended item. The function is intentionally simple and stable.
    """

    base_sim = compute_similarity_score(emp, item)
    # Mandatory items get a base floor probability boost, strategic slightly more engagement.
    prob = base_sim
    if item.is_mandatory:
        prob = max(prob, 0.35)
    if item.is_strategic:
        prob += 0.05
    # Clamp into [0, 0.95]
    prob = max(0.0, min(0.95, prob))
    return prob


def build_item_index(items: Sequence[CatalogItem]) -> Dict[str, CatalogItem]:
    return {it.item_id: it for it in items}
