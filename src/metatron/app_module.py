"""Every bounded context's module, in one list: the analog of Nest's AppModule."""

from metatron.config.config_module import config_module
from metatron.scan.scan_module import scan_module

app_modules = (
    config_module,
    scan_module,
)
