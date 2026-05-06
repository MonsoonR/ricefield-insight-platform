from __future__ import annotations

import itertools
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.schemas.data_model import Plot, PlotGeoJsonReport


PLOT_CODE_PROPERTY_KEYS = ("plot_code", "id", "name", "编号", "地块编号")
ALIAS_PROPERTY_KEYS = ("alias", "aliases", "plot_alias", "别名", "地块别名")
REGION_PROPERTY_KEYS = ("region", "area", "区域", "所属区域")
REGION_NAME_MAP = {
    "east": "东区",
    "dong": "东区",
    "东": "东区",
    "东区": "东区",
    "west": "西区",
    "xi": "西区",
    "西": "西区",
    "西区": "西区",
}
MOJIBAKE_MARKERS = ("�", "锛", "鈥", "Ã", "å", "æ", "ç")


@dataclass(frozen=True)
class PlotGeoJsonResult:
    plots: list[Plot]
    plot_aliases: dict[str, list[str]]
    report: PlotGeoJsonReport


def parse_geojson_directory(
    geojson_dir: str | Path,
    *,
    excel_plot_codes: list[str] | set[str] | tuple[str, ...] | None = None,
) -> PlotGeoJsonResult:
    directory = Path(geojson_dir)
    geojson_files = sorted(directory.glob("*.geojson"))

    plots: list[Plot] = []
    plot_aliases: dict[str, list[str]] = {}
    duplicate_plot_codes: list[str] = []
    garbled_plot_codes: list[str] = []
    seen_plot_keys: dict[tuple[str | None, str], Plot] = {}
    source_files: list[str] = []
    total_feature_count = 0

    for geojson_file in geojson_files:
        source_files.append(geojson_file.name)
        with geojson_file.open("r", encoding="utf-8") as file:
            collection = json.load(file)

        collection_region = _infer_region(collection, geojson_file)
        features = collection.get("features", [])
        if not isinstance(features, list):
            continue
        total_feature_count += len(features)

        for feature in features:
            if not isinstance(feature, dict):
                continue
            properties = feature.get("properties") or {}
            if not isinstance(properties, dict):
                properties = {}

            raw_code = _first_property(properties, PLOT_CODE_PROPERTY_KEYS)
            if raw_code is None:
                continue
            if _looks_garbled(raw_code):
                _append_unique(garbled_plot_codes, str(raw_code))
                continue

            region = _infer_region(feature, geojson_file) or collection_region
            aliases = _collect_aliases(raw_code, properties)
            if not aliases:
                continue

            plot_code = aliases[0]
            plot_key = (region, plot_code)
            duplicate_label = _plot_report_label(region, plot_code)
            if plot_key in seen_plot_keys:
                existing_plot = seen_plot_keys[plot_key]
                existing_plot.status = "duplicate"
                _append_unique(duplicate_plot_codes, duplicate_label)
                _merge_aliases(existing_plot.aliases, aliases)
                _index_aliases(plot_aliases, existing_plot.plot_id, existing_plot.aliases)
                continue

            plot = Plot(
                plot_id=_plot_id(region, plot_code),
                plot_code=plot_code,
                aliases=aliases,
                plot_name=str(raw_code).strip(),
                region=region,
                geometry=feature.get("geometry"),
                status="normal",
            )
            plots.append(plot)
            seen_plot_keys[plot_key] = plot
            _index_aliases(plot_aliases, plot.plot_id, plot.aliases)

    matched_plot_ids: set[str] = set()
    unmatched_excel_plots: list[str] = []
    if excel_plot_codes is not None:
        for raw_excel_code in excel_plot_codes:
            normalized = normalize_plot_code(raw_excel_code)
            matched_ids = plot_aliases.get(normalized)
            if not matched_ids:
                _append_unique(unmatched_excel_plots, str(raw_excel_code))
                continue
            matched_plot_ids.add(matched_ids[0])

    geojson_plots_without_excel_data: list[str] = []
    if excel_plot_codes is not None:
        for plot in plots:
            if plot.plot_id in matched_plot_ids or plot.status == "invalid_code":
                continue
            if plot.status == "normal":
                plot.status = "no_data"
            _append_unique(
                geojson_plots_without_excel_data,
                _plot_report_label(plot.region, plot.plot_code),
            )

    report = PlotGeoJsonReport(
        source_files=source_files,
        total_feature_count=total_feature_count,
        parsed_plot_count=len(plots),
        duplicate_plot_codes=duplicate_plot_codes,
        garbled_plot_codes=garbled_plot_codes,
        unmatched_excel_plots=unmatched_excel_plots,
        geojson_plots_without_excel_data=geojson_plots_without_excel_data,
    )
    return PlotGeoJsonResult(
        plots=plots,
        plot_aliases=_sorted_alias_map(plot_aliases),
        report=report,
    )


def build_plot_lookup(plots: list[Plot]) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for plot in plots:
        for alias in plot.aliases or [plot.plot_code]:
            lookup.setdefault(alias, plot.plot_id)
    return dict(sorted(lookup.items()))


def normalize_plot_code(value: object, *, region: str | None = None) -> str:
    del region
    text = _normalize_text(value)
    match = re.fullmatch(r"([A-Z]?\d+[A-Z]+)-\d+", text)
    if match:
        return match.group(1)
    return text


def _collect_aliases(raw_code: object, properties: dict[str, Any]) -> list[str]:
    aliases: list[str] = []
    for alias in _expand_plot_code(raw_code):
        _append_unique(aliases, alias)

    for key in ALIAS_PROPERTY_KEYS:
        raw_alias = properties.get(key)
        if raw_alias is None:
            continue
        if isinstance(raw_alias, list):
            raw_values = raw_alias
        else:
            raw_values = re.split(r"[,;，；]", str(raw_alias))
        for value in raw_values:
            if _looks_garbled(value):
                continue
            for alias in _expand_plot_code(value):
                _append_unique(aliases, alias)

    return aliases


def _expand_plot_code(value: object) -> list[str]:
    text = _normalize_text(value)
    if not text:
        return []
    segment_options = [_expand_segment(segment) for segment in text.split("-")]
    aliases = ["-".join(parts) for parts in itertools.product(*segment_options)]
    return [normalize_plot_code(alias) for alias in aliases if alias]


def _expand_segment(segment: str) -> list[str]:
    parts = [part for part in segment.split("/") if part]
    if len(parts) <= 1:
        return parts

    first = parts[0]
    prefix_match = re.match(r"(\d+)", first)
    numeric_prefix = prefix_match.group(1) if prefix_match else ""
    expanded: list[str] = []
    for part in parts:
        if numeric_prefix and not re.match(r"\d", part):
            expanded.append(f"{numeric_prefix}{part}")
        else:
            expanded.append(part)
    return expanded


def _index_aliases(
    plot_aliases: dict[str, list[str]],
    plot_id: str,
    aliases: list[str],
) -> None:
    for alias in aliases:
        if alias not in plot_aliases:
            plot_aliases[alias] = []
        _append_unique(plot_aliases[alias], plot_id)


def _merge_aliases(existing_aliases: list[str], new_aliases: list[str]) -> None:
    for alias in new_aliases:
        _append_unique(existing_aliases, alias)


def _first_property(properties: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        value = properties.get(key)
        if value not in (None, ""):
            return value
    return None


def _infer_region(data: dict[str, Any], file_path: Path) -> str | None:
    properties = data.get("properties") or {}
    if isinstance(properties, dict):
        raw_region = _first_property(properties, REGION_PROPERTY_KEYS)
        region = _region_from_text(raw_region)
        if region is not None:
            return region

    for value in (data.get("name"), file_path.stem):
        region = _region_from_text(value)
        if region is not None:
            return region
    return None


def _region_from_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip().lower()
    return REGION_NAME_MAP.get(text)


def _normalize_text(value: object) -> str:
    if value is None:
        return ""
    text = unicodedata.normalize("NFKC", str(value))
    text = text.strip().strip("{}").strip().strip('"').strip("'")
    text = re.sub(r"\s+", "", text)
    text = text.replace("—", "-").replace("–", "-").replace("_", "-")
    return text.upper()


def _looks_garbled(value: object) -> bool:
    text = str(value)
    return any(marker in text for marker in MOJIBAKE_MARKERS)


def _plot_id(region: str | None, plot_code: str) -> str:
    return f"{_region_slug(region)}-{plot_code}"


def _region_slug(region: str | None) -> str:
    if region == "东区":
        return "east"
    if region == "西区":
        return "west"
    return "unknown"


def _plot_report_label(region: str | None, plot_code: str) -> str:
    return f"{region or '未知区域'}:{plot_code}"


def _append_unique(values: list[str], value: str) -> None:
    if value not in values:
        values.append(value)


def _sorted_alias_map(plot_aliases: dict[str, list[str]]) -> dict[str, list[str]]:
    return {alias: plot_aliases[alias] for alias in sorted(plot_aliases)}
