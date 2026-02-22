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
    CorrEmail: str = ""          # فیلد جدید
    ArtAffiliations: str = ""
    ArtLicense: str = ""
    ArtPdfLink: str = ""
    ArtFileName: str = ""
    ArtKeywords: str = ""
    MeshTerms: str = ""           # فیلد جدید
    PubHistory: str = ""
    FundingGrant: str = ""
    FundingId: str = ""           # فیلد جدید
    EthicsStatement: str = ""     # فیلد جدید
    OrcidIds: str = ""            # فیلد جدید (لیست ORCIDها)
    CustomMeta: str = ""
    ArtReferences: str = ""
    Animal: bool = False

    def to_dict(self):
        return self.__dict__