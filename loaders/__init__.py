from typing import Dict

from loaders.base import BaseReportLoader
from loaders.paypal_loader import PaypalActivityReportLoader
from loaders.fin_loader import FinReportLoader

# folder name -> report loader
loaders: Dict[str, BaseReportLoader] = {
    'paypal_activity_reports': PaypalActivityReportLoader(),
    'fin_reports': FinReportLoader(),
    # Add more report loaders here
}

__all__ = ["loaders"]
