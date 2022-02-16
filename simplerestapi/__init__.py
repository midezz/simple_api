from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import  AsyncSession

Session = sessionmaker(expire_on_commit=False, class_=AsyncSession)
