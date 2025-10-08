from . import average_rating, average_price

AVAILABLE_REPORTS = {
    "average-rating": average_rating,
}

def get_report_module(report_name):
    if report_name not in AVAILABLE_REPORTS:
        raise ValueError(f"Unknown report: {report_name}")
    return AVAILABLE_REPORTS[report_name]