from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class ArticleModel:
    ArticlesID: int = 0
    ArtTitle: str = ""
    ArtBody: str = ""
    ArtAbstract: str = ""
    PubDate: datetime = datetime.min
    ArtLanguage: str = ""
    PmId: Optional[int] = None
    BankId: Optional[int] = None
    BankNo: int = 0
    ArtDoi: str = ""
    ArtType: str = ""
    JournalTitle: str = ""
    JournalAbbrev: str = ""
    ArtPublisher: str = ""
    ArtVolume: str = ""
    ArtIssue: str = ""
    ArtFpage: str = ""
    ArtPageRange: str = ""
    ArtAuthors: str = ""
    CorrespondingAuthor: str = ""
    CorrEmail: str = ""
    ArtAffiliations: str = ""
    ArtLicense: str = ""
    ArtPdfLink: str = ""
    ArtFileName: str = ""
    ArtKeywords: str = ""
    MeshTerms: str = ""
    PubHistory: str = ""
    FundingGrant: str = ""
    FundingId: str = ""
    EthicsStatement: str = ""
    OrcidIds: str = ""
    CustomMeta: str = ""
    ArtReferences: str = ""
    NonTarget: bool = False

    def to_dict(self):
        return self.__dict__