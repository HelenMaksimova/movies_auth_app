from datetime import UTC, datetime, timedelta
from hashlib import sha256
from os import environ
from secrets import token_hex
from typing import Self
from uuid import UUID, uuid4

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from sqlalchemy import (
    DateTime,
    ForeignKey,
    LargeBinary,
    String,
    Text,
    and_,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)
from sqlalchemy.orm.relationships import foreign

from src.models.pg_base import Base

__all__ = (
    "Realm",
    "RealmCredentials",
    "RealmKeys",
)


class RealmCredentials(MappedAsDataclass, Base):
    __tablename__ = "realm_credentials"

    token: Mapped[str] = mapped_column(String(64), primary_key=True)
    realm_id: Mapped[UUID] = mapped_column(ForeignKey("realm.id"))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(tz=UTC),
        default=func.now(tz=UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(tz=UTC),
        default=func.now(tz=UTC),
    )

    @classmethod
    def generate_token(cls) -> str:
        return token_hex(32)

    @classmethod
    def hash_token(cls, token: str) -> str:
        return sha256(token.encode()).hexdigest()

    @classmethod
    def create_credentials(
        cls, realm_id: UUID, expires_in: int = 30
    ) -> tuple[str, Self]:
        current_date = datetime.now(UTC)
        token = cls.generate_token()
        token_hash = cls.hash_token(token)

        credentials = cls(
            token=token_hash,
            realm_id=realm_id,
            expires_at=current_date + timedelta(days=expires_in),
            created_at=current_date,
            updated_at=current_date,
        )
        return token, credentials

    def is_valid(self):
        return self.is_active and self.expires_at > datetime.now(UTC)

    def revoke(self):
        self.is_active = False
        self.revoked_at = datetime.now(UTC)


class RealmKeys(MappedAsDataclass, Base):
    __tablename__ = "realm_keys"

    realm_id: Mapped[UUID] = mapped_column(ForeignKey("realm.id"))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    public_key: Mapped[str] = mapped_column(Text)
    private_key_encrypted: Mapped[bytes] = mapped_column(LargeBinary)
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    is_active: Mapped[bool] = mapped_column(default=True)
    id: Mapped[UUID] = mapped_column(primary_key=True, default_factory=uuid4)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(tz=UTC),
        default=func.now(tz=UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(tz=UTC),
        default=func.now(tz=UTC),
    )

    def is_valid(self):
        return self.is_active and self.expires_at > datetime.now(UTC)

    def revoke(self):
        self.is_active = False
        self.revoked_at = datetime.now(UTC)

    @property
    def private_key(self) -> str:
        return self.cipher().decrypt(self.private_key_encrypted).decode()

    @classmethod
    def cipher(cls) -> Fernet:
        master_key = environ.get("FERNET_MASTER_KEY")
        if not master_key:
            raise RuntimeError("FERNET_MASTER_KEY is not set in environment")
        return Fernet(master_key)

    @classmethod
    def create_keys(cls, realm_id: UUID, expires_in: int = 30) -> Self:
        current_date = datetime.now(UTC)
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048
        )
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode()

        return cls(
            realm_id=realm_id,
            expires_at=current_date + timedelta(days=expires_in),
            public_key=public_pem,
            private_key_encrypted=cls.cipher().encrypt(private_pem),
            created_at=current_date,
            updated_at=current_date,
        )


class Realm(MappedAsDataclass, Base):
    __tablename__ = "realm"

    name: Mapped[str] = mapped_column(unique=True)
    credentials: Mapped[list["RealmCredentials"]] = relationship(
        "RealmCredentials",
        lazy="selectin",
        primaryjoin=lambda: and_(
            foreign(RealmCredentials.realm_id) == Realm.id,
            RealmCredentials.is_active,
            RealmCredentials.revoked_at.is_(None),
            RealmCredentials.expires_at > datetime.now(UTC),
        ),
        order_by="RealmCredentials.expires_at",
        viewonly=True,
    )

    keys: Mapped[list["RealmKeys"]] = relationship(
        "RealmKeys",
        lazy="selectin",
        primaryjoin=lambda: and_(
            foreign(RealmKeys.realm_id) == Realm.id,
            RealmKeys.is_active,
            RealmKeys.revoked_at.is_(None),
            RealmKeys.expires_at > datetime.now(UTC),
        ),
        order_by="RealmKeys.expires_at",
        viewonly=True,
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default_factory=uuid4)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(tz=UTC),
        default=func.now(tz=UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(tz=UTC),
        default=func.now(tz=UTC),
    )
