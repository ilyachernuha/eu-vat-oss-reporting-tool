from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd

from logger import logger


class BaseReportLoader(ABC):

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

            logger.info(f'Loading report: {file.name}')
            dataframes.append(self.load_report(Path(file)))

        return pd.concat(dataframes, ignore_index=True)

    @staticmethod
    def load_dataframe_from_file(filepath: str | Path, **kwargs) -> pd.DataFrame:
        filepath = Path(filepath)
        ext = filepath.suffix.lower()

        if ext == '.csv':
            return pd.read_csv(filepath, **kwargs)
        elif ext in {'.xlsx', '.xls'}:
            return pd.read_excel(filepath, **kwargs)

        raise ValueError(f'Unsupported file extension: {ext}')
