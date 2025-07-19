from pydantic_settings import BaseSettings

class Settings(BaseSettings):  # pyright: ignore[reportGeneralTypeIssues]
    # 主数据库路径
    DATABASE_PATH: str = "karate.db"
    # 比赛过程信息数据库路径
    MATCH_DATABASE_PATH: str = "matches.db"
    
    class Config:
        # 指定环境变量文件名，可自动读取 .env 文件中的配置
        env_file = ".env"