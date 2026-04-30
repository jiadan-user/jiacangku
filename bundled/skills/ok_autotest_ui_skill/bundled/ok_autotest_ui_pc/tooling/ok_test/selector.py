from __future__ import annotations

import argparse

from .catalog import load_catalog
from .common import slugify
from .models import CatalogCase, SelectionCriteria


def _matches_value(candidate: str | None, expected: str | None) -> bool:
    if not expected:
        return True
    if not candidate:
        return False
    return slugify(candidate) == slugify(expected)


def _matches_aliases(case: CatalogCase, value: str | None) -> bool:
    if not value:
        return True
    target = slugify(value)
    return target in {slugify(alias) for alias in case.aliases + [case.module_id or "", case.feature_id or ""]}


def select_cases(criteria: SelectionCriteria) -> list[CatalogCase]:
    return select_cases_from_catalog(load_catalog(), criteria)


def select_cases_from_catalog(catalog: list[CatalogCase], criteria: SelectionCriteria) -> list[CatalogCase]:
    selected: list[CatalogCase] = []
    for case in catalog:
        if case.skill_excluded:
            continue
        if not _matches_aliases(case, criteria.module):
            continue
        if criteria.module and slugify(case.module_id or "") != slugify(criteria.module):
            if not _matches_aliases(case, criteria.module):
                continue
        if criteria.feature and slugify(case.feature_id or "") != slugify(criteria.feature):
            if not _matches_aliases(case, criteria.feature):
                continue
        if criteria.story and slugify(case.allure_story or "") != slugify(criteria.story):
            continue
        if not _matches_value(case.priority, criteria.priority):
            continue
        if not _matches_value(case.site, criteria.site):
            continue
        if criteria.case_id and slugify(case.case_id or "") != slugify(criteria.case_id):
            continue
        if criteria.path and criteria.path not in case.file_path:
            continue
        if criteria.nodeid and criteria.nodeid not in case.nodeid:
            continue
        selected.append(case)
    return selected


def build_criteria(args: argparse.Namespace) -> SelectionCriteria:
    return SelectionCriteria(
        module=args.module,
        feature=args.feature,
        story=args.story,
        priority=args.priority,
        site=args.site,
        case_id=args.case_id,
        path=args.path,
        nodeid=args.nodeid,
        dry_run=getattr(args, "dry_run", False),
    )


def handle_list(args: argparse.Namespace) -> int:
    criteria = build_criteria(args)
    selected = select_cases(criteria)
    print(f"matched_cases={len(selected)}")
    for case in selected:
        print(
            " | ".join(
                [
                    case.nodeid,
                    case.case_id or "-",
                    case.module_id or "-",
                    case.feature_id or "-",
                    case.priority or "-",
                    case.site or "-",
                    case.allure_title or case.test_name,
                ]
            )
        )
    return 0
