from pydantic import BaseModel, Field, constr
from datetime import datetime

class SyncCache(BaseModel):
    last_checked_time: datetime
    commit_hash: constr(pattern=r"^[a-f0-9]{40}$")
