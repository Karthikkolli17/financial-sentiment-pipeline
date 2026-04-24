import pandas as pd
from evidently import ColumnMapping # tells which columns are numerical, which are text, which is the target
from evidently.report import Report # the object that runs the analysis and generates the HTML output
from evidently.metric_preset import DataDriftPreset # a pre-built set of drift checks for comparing two datasets

SENTIMENT_COLUMNS = [
    "vader_compound",
    "vader_positive",
    "vader_neutral",
    "vader_negative",
    "textblob_polarity",
    "textblob_subjectivity",
]

# reference_df = old historical articles
# current_df = latest new fetched and scored articles
# report_path = where to save HMTL report file
def run_drift_report(reference_df, current_df, report_path):

    columnMapping = ColumnMapping(numerical_features = SENTIMENT_COLUMNS)

    report = Report(metrics = [DataDriftPreset()])
    ref = reference_df[SENTIMENT_COLUMNS].dropna()                                                        
    cur = current_df[SENTIMENT_COLUMNS].dropna()                                                          
    report.run(reference_data=ref, current_data=cur, column_mapping=columnMapping)

    report.save_html(report_path)
    return report.as_dict()