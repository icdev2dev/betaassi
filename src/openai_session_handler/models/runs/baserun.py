from typing import Optional
from pydantic import Field

from .metarun import MetaRun


class BaseRun(MetaRun):
    run_type:Optional[str] = Field(default="")
