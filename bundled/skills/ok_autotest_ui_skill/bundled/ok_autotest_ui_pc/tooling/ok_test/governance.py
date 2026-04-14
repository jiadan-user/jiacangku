from __future__ import annotations

from collections import defaultdict

from .common import slugify
from .models import BASELINE_MARKERS, CatalogCase, PRIORITY_ORDER, SelectionCriteria


def case_is_governed(case: CatalogCase) -> bool:
    return bool(case.module_id and case.feature_id and case.priority and case.case_id)


def priority_rank(priority: str | None) -> int:
    if priority not in PRIORITY_ORDER:
        return len(PRIORITY_ORDER) + 1
    return PRIORITY_ORDER.index(priority)


def is_baseline_case(case: CatalogCase) -> bool:
    if case.baseline_set:
        return True
    if case.priority == "p0":
        return True
    marker_set = set(case.markers)
    return bool(marker_set & BASELINE_MARKERS)


def matches_case(case: CatalogCase, criteria: SelectionCriteria, ignore_priority: bool = False) -> bool:
    def _matches(candidate: str | None, expected: str | None) -> bool:
        if not expected:
            return True
        return slugify(candidate) == slugify(expected)

    if criteria.module and slugify(case.module_id or "") != slugify(criteria.module):
        aliases = {slugify(alias) for alias in case.aliases + [case.module_id or ""]}
        if slugify(criteria.module) not in aliases:
            return False
    if criteria.feature and slugify(case.feature_id or "") != slugify(criteria.feature):
        aliases = {slugify(alias) for alias in case.aliases + [case.feature_id or ""]}
        if slugify(criteria.feature) not in aliases:
            return False
    if criteria.story and not _matches(case.allure_story, criteria.story):
        return False
    if not ignore_priority and criteria.priority and not _matches(case.priority, criteria.priority):
        return False
    if criteria.site and not _matches(case.site, criteria.site):
        return False
    if criteria.case_id and not _matches(case.case_id, criteria.case_id):
        return False
    if criteria.path and criteria.path not in case.file_path:
        return False
    if criteria.nodeid and criteria.nodeid not in case.nodeid:
        return False
    return True


def scope_cases(
    catalog: list[CatalogCase],
    selection: SelectionCriteria,
    module_filter: str | None = None,
    selected_nodeids: set[str] | None = None,
) -> list[CatalogCase]:
    catalog = [case for case in catalog if not case.skill_excluded]
    if module_filter:
        return [case for case in catalog if slugify(case.module_id or "") == slugify(module_filter)]

    scoped = [case for case in catalog if matches_case(case, selection, ignore_priority=True)]
    if scoped:
        return scoped

    if selected_nodeids:
        return [case for case in catalog if case.nodeid in selected_nodeids]
    return catalog


def recommend_cases(
    catalog: list[CatalogCase],
    selection: SelectionCriteria,
    selected_cases: list[CatalogCase],
) -> tuple[list[CatalogCase], list[CatalogCase], list[CatalogCase]]:
    selected_nodeids = {case.nodeid for case in selected_cases}
    scoped_cases = scope_cases(catalog, selection, selected_nodeids=selected_nodeids)
    baseline_cases = [case for case in scoped_cases if is_baseline_case(case)]

    if selection.priority:
        threshold = priority_rank(selection.priority)
        recommended = [
            case for case in scoped_cases
            if priority_rank(case.priority) <= threshold or case.nodeid in {item.nodeid for item in baseline_cases}
        ]
    else:
        recommended_map = {case.nodeid: case for case in selected_cases}
        for case in baseline_cases:
            recommended_map[case.nodeid] = case
        recommended = sorted(recommended_map.values(), key=lambda item: item.nodeid)

    baseline_map = {case.nodeid: case for case in baseline_cases}
    selected_map = {case.nodeid: case for case in selected_cases}
    for case in baseline_cases:
        selected_map.setdefault(case.nodeid, case)

    return scoped_cases, recommended, sorted(baseline_map.values(), key=lambda item: item.nodeid)


def feature_breakdown_template() -> dict[str, dict[str, int]]:
    return defaultdict(lambda: defaultdict(int))
