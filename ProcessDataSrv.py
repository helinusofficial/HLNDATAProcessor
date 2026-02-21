import os
import re
from lxml import etree
from datetime import datetime
from unstructured.cleaners.core import clean, clean_extra_whitespace
from ArticleModel import ArticleModel


class ProcessDataSrv:
    animal_keywords = [
        # موش‌ها و رت‌ها
        "mouse", "mice", "rat", "sprague dawley", "wistar", "long evans",
        # خرگوش‌ها
        "rabbit", "rabbits",
        # سگ‌ها و گربه‌ها
        "dog", "dogs", "cat", "cats",
        # ماهی و آبزیان
        "zebrafish", "danio rerio", "frog", "xenopus", "fish", "salmon",
        # حشرات و مدل‌های ساده
        "fly", "drosophila", "bee", "mosquito",
        # کرم‌ها و نماتدها
        "c. elegans", "caenorhabditis elegans", "worm",
        # مخمرها و قارچ‌ها
        "yeast", "saccharomyces cerevisiae",
        # دیگر پستانداران آزمایشگاهی
        "guinea pig", "hamster", "gerbil", "ferret",
        # پرندگان
        "chicken", "quail", "duck",
        # آبزیان کوچک آزمایشگاهی
        "xenopus laevis", "xenopus tropicalis",
        # مدل‌های آزمایشگاهی کمتر رایج
        "pig", "minipig", "sheep", "goat", "cow", "calf", "horse", "rabbit"
    ]
    @staticmethod
    def process_file(file_path: str) -> ArticleModel:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        try:
            parser = etree.XMLParser(recover=True, remove_comments=True)
            tree = etree.parse(file_path, parser=parser)
            root = tree.getroot()

            article = ArticleModel()
            article.BankNo=1  #1=PMC
            article.ArtFileName = os.path.basename(file_path)

            article.JournalTitle = ProcessDataSrv._get_text(root, ".//journal-title")
            article.JournalAbbrev = ProcessDataSrv._get_text(
                root, ".//journal-id[@journal-id-type='nlm-ta'] | .//abbrev-journal-title"
            )
            article.ArtPublisher = ProcessDataSrv._get_text(root, ".//publisher-name")

            article.ArtTitle = ProcessDataSrv._get_text(root, ".//article-title")
            article.ArtDoi = ProcessDataSrv._get_text(root, ".//article-id[@pub-id-type='doi']")
            article.ArtType = root.get("article-type", "")
            article.ArtLanguage = ProcessDataSrv._get_text(root, ".//language") or "en"

            pmid = ProcessDataSrv._get_text(root, ".//article-id[@pub-id-type='pmid']")
            article.PmId = int(pmid) if pmid.isdigit() else None

            pmc = ProcessDataSrv._get_text(root, ".//article-id[@pub-id-type='pmc']")
            if pmc:
                pmc_clean = pmc.upper().replace('PMC', '').strip()
                article.BankId = int(pmc_clean) if pmc_clean.isdigit() else None

            article.ArtVolume = ProcessDataSrv._get_text(root, ".//volume")
            article.ArtIssue = ProcessDataSrv._get_text(root, ".//issue")
            article.ArtFpage = ProcessDataSrv._get_text(root, ".//fpage")
            lpage = ProcessDataSrv._get_text(root, ".//lpage")
            if article.ArtFpage and lpage:
                article.ArtPageRange = f"{article.ArtFpage}-{lpage}"

            pub_date_nodes = root.xpath(
                ".//pub-date[@pub-type='ppub'] | .//pub-date[@pub-type='epub'] | .//pub-date"
            )
            if pub_date_nodes:
                node = pub_date_nodes[0]
                year = ProcessDataSrv._get_text(node, "year")
                month = ProcessDataSrv._get_text(node, "month")
                day = ProcessDataSrv._get_text(node, "day")

                if year.isdigit():
                    try:
                        m = int(month) if month and month.isdigit() and 1 <= int(month) <= 12 else 1
                        d = int(day) if day and day.isdigit() and 1 <= int(day) <= 31 else 1
                        article.PubDate = datetime(int(year), m, d)
                    except (ValueError, TypeError):
                        pass

            authors = []
            for auth in root.xpath(".//contrib[@contrib-type='author']"):
                given = ProcessDataSrv._get_text(auth, './/given-names')
                sur = ProcessDataSrv._get_text(auth, './/surname')
                name = f"{given} {sur}".strip()
                if name:
                    authors.append(name)
            article.ArtAuthors = ", ".join(authors)

            corr_auth = root.xpath(".//contrib[@contrib-type='author' and @corresp='yes']")
            if corr_auth:
                given = ProcessDataSrv._get_text(corr_auth[0], ".//given-names")
                sur = ProcessDataSrv._get_text(corr_auth[0], ".//surname")
                article.CorrespondingAuthor = f"{given} {sur}".strip()

            affs = [clean_extra_whitespace(" ".join(aff.itertext())) for aff in root.xpath(".//aff")]
            article.ArtAffiliations = " | ".join(filter(None, affs))

            keywords = [k.text.strip() for k in root.xpath(".//kwd") if k.text]
            article.ArtKeywords = ", ".join(keywords)
            article.ArtLicense = ProcessDataSrv._get_text(root, ".//license//p")

            body_node = root.find(".//body")
            if body_node is not None:
                raw_text = " ".join(body_node.itertext())
                content_to_check = " ".join([
                    article.ArtTitle or "",
                    article.ArtKeywords or "",
                    article.MainText or ""
                ]).lower()

                if any(k in content_to_check for k in ProcessDataSrv.animal_keywords):
                    article.Animal=True
                    return article

                cleaned = ProcessDataSrv._filter_figure_references(raw_text)
                article.MainText = clean(cleaned, extra_whitespace=True, dashes=True, bullets=False)
                article.MainText = clean_extra_whitespace(article.MainText).strip()

            refs = []
            for ref in root.xpath(".//ref"):
                ref_text = " ".join(ref.itertext()).strip()
                if ref_text:
                    refs.append(clean_extra_whitespace(ref_text))
            article.ArtReferences = " || ".join(refs)

            article.FundingGrant = " | ".join(
                [f.text.strip() for f in root.xpath(".//funding-source") if f.text]
            )

            article.ArtPdfLink = ProcessDataSrv._get_text(root, ".//self-uri[@content-type='pdf']/@href")
        except Exception:
            print(f"Error in ProcessDataSrv: {file_path}")
            return None

        return article

    @staticmethod
    def _get_text(node, xpath: str) -> str:
        try:
            res = node.xpath(xpath)
            if res:
                if isinstance(res[0], etree._Element):
                    return " ".join(res[0].itertext()).strip()
                return str(res[0]).strip()
        except Exception:
            pass
        return ""

    @staticmethod
    def _filter_figure_references(text: str) -> str:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return " ".join([
            s for s in sentences
            if not (
                re.search(r'(?i)\b(Fig|Table|Tbl)\.?\s*\d+', s)
                and len(s) < 65
            )
        ])