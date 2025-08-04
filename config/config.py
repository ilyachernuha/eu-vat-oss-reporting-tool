from config.config_types import Config


config: Config = {
    
    # Format: YYYY-MM-DD (last day of the quarter)
    'reporting_date': '2025-03-31',

    # Output file name
    'report_name': 'Q1 2025 VAT report', 

    # Input folder name with supported reports in corresponding subdirectories
    'input_folder': "input" 
    
}
