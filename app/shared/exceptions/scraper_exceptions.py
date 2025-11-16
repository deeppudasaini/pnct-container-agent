from app.shared.exceptions.base_exceptions import PNCTBaseException


class ScraperException(PNCTBaseException):
    """Base scraper exception"""
    pass


class BrowserError(ScraperException):
    """Browser initialization or operation error"""
    pass


class PageLoadError(ScraperException):
    """Page load error"""
    pass


class DataExtractionError(ScraperException):
    """Data extraction error"""
    pass


class CaptchaError(ScraperException):
    """CAPTCHA encountered"""
    pass


class ContainerNotFoundError(ScraperException):
    """Container not found on PNCT site"""
    pass
