from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd

from logger import logger


class BaseReportLoader(ABC):

    EXPECTED_COLUMNS = {
        'Date': 'datetime64[ns]',
        'Country Code': 'string',
        'Currency': 'string',
        'Gross Amount': 'float',
        'Legal Entity': 'string'
    }

    @abstractmethod
    def load_report(self, filepath: str | Path) -> pd.DataFrame:
        '''ReportLoaders must implement load_report() method.'''
        pass

    def load_folder(self, folder: str | Path) -> pd.DataFrame:

        dataframes = []
        for file in Path(folder).iterdir():

            if not file.is_file():
                logger.warning(f'Skipping subdirectory: {file}')
                continue

            if file.suffix.lower() not in ['.csv', '.xlsx', '.xls']:
                logger.warning(f'Skipping unsupported file: {file.name}')
                continue

            try:
                logger.info(f'Loading report: {file.name}')
                df = self.load_report(Path(file))
                self.validate_columns(df)
                dataframes.append(df)
            except Exception as e:
                logger.error(f'Failed to load report {file.name}: {e}')
                continue

        return pd.concat(dataframes, ignore_index=True)

    def validate_columns(self, df: pd.DataFrame) -> None:
        errors = []

        for column, expected_type in self.EXPECTED_COLUMNS.items():
            if column not in df.columns:
                errors.append(f"Column '{column}' is missing.")
                continue

            actual_dtype = df[column].dtype

            if expected_type == 'datetime64[ns]':
                if not pd.api.types.is_datetime64_any_dtype(df[column]):
                    errors.append(f"Column '{column}' is not datetime. Found: {actual_dtype}")

            elif expected_type == 'float':
                if not pd.api.types.is_float_dtype(df[column]):
                    errors.append(f"Column '{column}' is not float. Found: {actual_dtype}")

            elif expected_type == 'string':
                if not pd.api.types.is_string_dtype(df[column]):
                    errors.append(f"Column '{column}' is not string. Found: {actual_dtype}")

        if errors:
            raise TypeError("\nReport loader validation failed:\n" + "\n".join(errors))


    @staticmethod
    def load_dataframe_from_file(filepath: str | Path, **kwargs) -> pd.DataFrame:
        filepath = Path(filepath)
        ext = filepath.suffix.lower()

        if ext == '.csv':
            return pd.read_csv(filepath, **kwargs)
        elif ext in {'.xlsx', '.xls'}:
            return pd.read_excel(filepath, **kwargs)

        raise ValueError(f'Unsupported file extension: {ext}')
