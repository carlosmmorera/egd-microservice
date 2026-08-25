from pydantic import BaseModel

class BasicPlayer(BaseModel):
    retcode: str
    Pin_Player: int
    AGAID: str
    Last_Name: str
    Name: str
    Country_Code: str
    Club: str
    Grade: str
    Grade_n: int
    EGF_Placement: int
    Gor: int
    DGor: str
    Proposed_Grade: str
    Tot_Tournaments: int
    Last_Appearance: str
    Elab_Date: str
    Hidden_History: str
    Real_Last_Name: str
    Real_Name: str