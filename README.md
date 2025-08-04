# EU VAT OSS Reporting Script

## Description

This Python script simplifies the preparation of VAT returns under the European One Stop Shop (OSS) system. It calculates VAT payable amounts in EUR by processing sales data from various payment providers, applying country-specific VAT rates, and converting local currencies using ECB exchange rates.

### Key Features

* Automatically fetches effective **VAT rates** for all EU countries participating in the OSS scheme from [**Taxes in Europe Database v4**](https://ec.europa.eu/taxation_customs/tedb/#/home) published by **European Commission** .
* Retrieves **ECB foreign exchange (FOREX) rates** applicable on the reporting date from [**ECB Data Portal API**](https://data.ecb.europa.eu/help/api/overview) published by **European Central Bank**.
* Supports various report formats from different payment providers (e.g., PayPal, Fin). Support for other payment providers and report types can be easily added by implementing a custom loader (please see section **Adding Support for New Report Types** below).
* Calculates **VAT payable** based on the customer's country and the applicable VAT rate.
* Converts all reported amounts into **EUR** using official ECB exchange rates.
* Generates a summary MS Excel report with the following columns:

  * `Legal Entity`
  * `Customer's Country`
  * `Month`
  * `Total Sales Amount (Gross) in EUR`
  * `VAT Amount Payable in EUR`

---

## Requirements

* Python 3.8+
* Required packages listed in `requirements.txt` will be installed automatically

---

## Getting Started

### 1. Download the Script

Clone the repository or download it from [**HERE**](https://github.com/ilyachernuha/eu-vat-oss-reporting-tool/archive/refs/heads/main.zip).

### 2. Organize Input Files

Place raw data reports and mapping files into the corresponding subfolders within the `input` directory:

```
input/
├── paypal_activity_reports/
├── fin_reports/
├── mappings/
└── ...
```

### 3. Configure Reporting Parameters

Edit the `reporting_date` and `report_name` in the `config/config.py` file:

```python
# config/config.py

config: Config = {
  'reporting_date': '2025-03-31',  # Format: YYYY-MM-DD (last day of the quarter)
  'report_name': '1Q 2025 - VAT report'  # Output file name
}
```

### 4. Run the Script

From your terminal (within project root directory):

**On Windows (PowerShell):**

```powershell
.\run.ps1
```

**On macOS/Linux (bash):**

```bash
./run.sh
```

### 5. Retrieve the Report

The generated Excel report will be saved in the project root directory with the name specified in `report_name`.

---

## Adding Support for New Report Types

Currently supported providers: **PayPal**, **Fin**.

To integrate a new report type:

### 1. **Create a new input subdirectory** under `input/` using the desired name:

   ```
   input/new_report_type/
   ```

### 2. **Implement a loader:**

Create a new Python module in the `loaders` package and define a loader class that inherits from `BaseReportLoader`. Your loader must implement the method:

```python
def load_report(self, filepath: str | Path) -> pd.DataFrame: 
```

This method must load the report located at `filepath` and apply transformations required to return a DataFrame with **the following columns and types**:

| Column Name    | Data Type                     | Description                                                               |
| -------------- | ----------------------------- | ------------------------------------------------------------------------- |
| `Legal Entity` | `str`                         | Name of the legal entity making the sale                                  |
| `Date`         | `datetime`                    | Transaction date (`datetime.date` or `datetime64[ns]`)                    |
| `Country Code` | `str` (EU ISO 3166-1 alpha-2) | Must be a two-letter country code from the EU OSS scheme (see list below) |
| `Gross Amount` | `float`                       | Total gross sale amount in the buyer's **local currency**                 |
| `Currency`     | `str` (ISO 4217)              | Three-letter currency code (e.g. `EUR`, `USD`, `GBP`)                     |

#### Accepted Country Codes (`Country Code`):

Only the following **EU OSS participating country codes** are valid:

```
['AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'EL', 'ES', 'FI',
 'FR', 'UK', 'HR', 'HU', 'IE', 'IT', 'LT', 'LU', 'LV', 'MT', 'NL',
 'PL', 'PT', 'RO', 'SE', 'SI', 'SK', 'XI']
```

> * `EL` is the ISO code for **Greece** (used instead of `GR` in EU contexts).
> * `UK` and `XI` (Northern Ireland) are included for legacy or special VAT arrangements under OSS.
> * Any value not in this list will be ignored or raise an error during processing.

### 3. **Register the new loader**:

   * Open `loaders/__init__.py`
   * Add your new loader class to the `loaders` dictionary:

     ```python
     from loaders.new_loader import NewReportLoader # <-- import new loader

     loaders: Dict[str, BaseReportLoader] = {
       'paypal_activity_reports': PaypalActivityReportLoader(),
       'fin_reports': FinReportLoader(),
       'new_report_type': NewReportLoader()  # <-- register new loader
     }
     ```

---

## Notes

* Ensure input files follow the expected format; otherwise, parsing may fail.
* Script currently supports **EU OSS scheme only** (non-EU countries are ignored).