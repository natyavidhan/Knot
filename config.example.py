class Config:
    """Prefix for bot (Can be a string or a list)"""
    PREFIX = []
    """Cogs to be loaded"""
    INITIAL_COGS = (
        "cogs.error_handler",
        "cogs.info",
        "cogs.moderation",
        "cogs.fun",
        "cogs.events",
        "jishaku"

    )
    """Bot token"""
    TOKEN = ""
    """Logger webhook ( Must be a discord webhook url)"""
    WEBHOOK_URL = ""
    """Bot status"""
    STATUS = ""
    """MongoDB database URL"""
    DATABASE_URL = ""
    """Bittly access token"""
    BITTLY_ACCESS_TOKEN = ""
    """Youtube API key"""
    YOUTUBE_API_KEY = ""
    """Tenor Key"""
    TENOR_KEY = ""

    """Dev id (used for error pings and is_dev checks)"""
    DEV_ROLE_ID = 0
    """Channel to send welcome message"""
    WELCOME_CHANNEL = 0
    """Channel to send log messages"""
    LOGGING_CHANNEL = 0
    """Logger webhook embed colors"""
    LOG_COLOR = int("008000",base=16)
    WARNING_COLOR = int("DBA800",base=16)
    ERROR_COLOR = int("FF0000",base=16)

    """Bot embed colors"""
    EMBED_COLOR_GENERAL = int("ff7575", base=16)
    EMBED_COLOR_GREEN = int("ff7575", base=16)
    EMBED_COLOR_RED = int("ff7575", base=16)


