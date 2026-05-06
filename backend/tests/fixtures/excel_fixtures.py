from pathlib import Path

from openpyxl import Workbook


def create_observation_workbook(path: Path) -> Path:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "growth"
    sheet.append(["plot_code", "observed_at", "crop_growth", "plant_height"])
    sheet.append(["P001", "2026-05-01", 0.82, 82])
    sheet.append(["P001", "2026-05-02", None, 125])
    sheet.append(["P999", "2026-05-01", 0.75, 80])
    sheet.append(["P001", "not-a-date", 0.81, 83])
    sheet.append(["P001", "2026-05-03", "bad-value", 78])

    workbook.save(path)
    return path


def create_source_export_workbook(path: Path) -> Path:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "sheet1"
    sheet.append(["type", "地块", "时间", "data"])
    sheet.append(
        [
            "11",
            "baicheng-dong",
            "2026-05-01",
            '"P001":"0.82"',
            'P002:"1.25"',
            'P999:"0.7"',
            "broken-cell",
        ]
    )

    workbook.save(path)
    return path
