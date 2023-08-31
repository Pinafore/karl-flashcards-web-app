from pydantic import BaseModel

class TargetWindow(BaseModel):
    target_window_lowest: float
    target_window_highest: float
    target: float
