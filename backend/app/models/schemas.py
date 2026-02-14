class AnalyzeRequest(BaseModel):
    text: str


class Claim(BaseModel):
    claim: str
    status: str
    sources: list[str]


class AnalyzeResponse(BaseModel):
    credibility_score: int
    claims: list[Claim]
    summary: str
