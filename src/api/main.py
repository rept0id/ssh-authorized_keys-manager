from datetime import datetime, timezone
from enum import Enum
from typing import Annotated, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm.strategy_options import lazyload
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select

# class Hero(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     name: str = Field(index=True)
#     age: int | None = Field(default=None, index=True)
#     secret_name: str


class Host(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    address: str = Field(index=True)


class KeyType(str, Enum):
    RSA = "ssh-rsa"
    ECDSA_256 = "ecdsa-sha2-nistp256"
    ECDSA_384 = "ecdsa-sha2-nistp384"
    ECDSA_521 = "ecdsa-sha2-nistp521"
    ED25519 = "ssh-ed25519"
    RSA_SHA2_256 = "rsa-sha2-256"
    RSA_SHA2_512 = "rsa-sha2-512"


class Key(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    type: KeyType = Field(index=True)
    key: str = Field()
    comment: str | None = Field()


class Authorization(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created: datetime = Field(default=datetime.now(timezone.utc))
    modified: datetime = Field(default=datetime.now(timezone.utc))

    host_id: int = Field(foreign_key="host.id")
    key_id: int = Field(foreign_key="key.id")
    login_name: str = Field()

    comment: Optional[str] = Field(default=None)


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# @app.post("/heroes/")
# def create_hero(hero: Hero, session: SessionDep) -> Hero:
#     session.add(hero)
#     session.commit()
#     session.refresh(hero)
#     return hero


# @app.get("/heroes/")
# def read_heroes(
#     session: SessionDep,
#     offset: int = 0,
#     limit: Annotated[int, Query(le=100)] = 100,
# ) -> list[Hero]:
#     heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
#     return heroes


# @app.get("/heroes/{hero_id}")
# def read_hero(hero_id: int, session: SessionDep) -> Hero:
#     hero = session.get(Hero, hero_id)
#     if not hero:
#         raise HTTPException(status_code=404, detail="Hero not found")
#     return hero


# @app.delete("/heroes/{hero_id}")
# def delete_hero(hero_id: int, session: SessionDep):
#     hero = session.get(Hero, hero_id)
#     if not hero:
#         raise HTTPException(status_code=404, detail="Hero not found")
#     session.delete(hero)
#     session.commit()
#     return {"ok": True}


@app.post("/hosts/", response_model=Host)
def create_host(host: Host, session: SessionDep) -> Host:
    session.add(host)
    session.commit()
    session.refresh(host)
    return host


@app.get("/hosts/", response_model=List[Host])
def read_hosts(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> List[Host]:
    hosts = session.exec(select(Host).offset(offset).limit(limit)).all()
    return hosts


@app.get("/hosts/{host_id}", response_model=Host)
def read_host(host_id: int, session: SessionDep) -> Host:
    host = session.get(Host, host_id)
    if not host:
        raise HTTPException(status_code=404, detail="Host not found")
    return host


@app.get("/hosts/{host_id}/authorizations/", response_model=List[Authorization])
def read_authorizations_by_host(
    host_id: int, session: SessionDep
) -> List[Authorization]:
    host = session.get(Host, host_id)
    if not host:
        raise HTTPException(status_code=404, detail="Host not found")
    return host.authorizations


@app.delete("/hosts/{host_id}")
def delete_host(host_id: int, session: SessionDep):
    host = session.get(Host, host_id)
    if not host:
        raise HTTPException(status_code=404, detail="Host not found")
    session.delete(host)
    session.commit()
    return {"ok": True}


@app.post("/keys/", response_model=Key)
def create_key(key: Key, session: SessionDep) -> Key:
    session.add(key)
    session.commit()
    session.refresh(key)
    return key


@app.get("/keys/", response_model=List[Key])
def read_keys(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> List[Key]:
    keys = session.exec(select(Key).offset(offset).limit(limit)).all()
    return keys


@app.get("/keys/{key_id}", response_model=Key)
def read_key(key_id: int, session: SessionDep) -> Key:
    key = session.get(Key, key_id)
    if not key:
        raise HTTPException(status_code=404, detail="Key not found")
    return key


@app.delete("/keys/{key_id}")
def delete_key(key_id: int, session: SessionDep):
    key = session.get(Key, key_id)
    if not key:
        raise HTTPException(status_code=404, detail="Key not found")
    session.delete(key)
    session.commit()
    return {"ok": True}


@app.get("/keys/{key_id}/authorizations/", response_model=List[Authorization])
def read_authorizations_by_key(key_id: int, session: SessionDep) -> List[Authorization]:
    key = session.get(Key, key_id)
    if not key:
        raise HTTPException(status_code=404, detail="Key not found")
    return key.authorizations


@app.post("/authorizations/", response_model=Authorization)
def create_authorization(
    authorization: Authorization, session: SessionDep
) -> Authorization:
    session.add(authorization)
    session.commit()
    session.refresh(authorization)
    return authorization


@app.get("/authorizations/", response_model=List[Authorization])
def read_authorizations(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> List[Authorization]:
    authorizations = session.exec(
        select(Authorization).offset(offset).limit(limit)
    ).all()
    return authorizations


@app.get("/authorizations/{authorization_id}", response_model=Authorization)
def read_authorization(authorization_id: int, session: SessionDep) -> Authorization:
    authorization = session.get(Authorization, authorization_id)
    if not authorization:
        raise HTTPException(status_code=404, detail="Authorization not found")
    return authorization


@app.delete("/authorizations/{authorization_id}")
def delete_authorization(authorization_id: int, session: SessionDep):
    authorization = session.get(Authorization, authorization_id)
    if not authorization:
        raise HTTPException(status_code=404, detail="Authorization not found")
    session.delete(authorization)
    session.commit()
    return {"ok": True}
