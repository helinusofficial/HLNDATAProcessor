from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class ArticleModel:
    ArticlesID: int = 0
    ArtTitle: str = ""
    MainText: str = ""
    PubDate: datetime = datetime.min
    ArtLanguage: str = ""
    Pmid: Optional[int] = None
    Pmcaid_Pmcaiid: Optional[int] = None
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
    ArtAffiliations: str = ""
    ArtLicense: str = ""
    ArtPdfLink: str = ""
    ArtFileName: str = ""
    ArtKeywords: str = ""
    PubHistory: str = ""
    FundingGrant: str = ""
    CustomMeta: str = ""
    ArtReferences: str = ""

    def to_dict(self):
        """تبدیل مدل به دیکشنری برای درج راحت در دیتابیس یا تبدیل به JSON"""
        return self.__dict__