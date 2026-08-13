import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile

from app.core.config import settings

ALLOWED_CHALLENGE_FILE_EXTENSIONS = frozenset(
    {".raw", ".pcap", ".dd", ".png", ".txt", ".pkz", ".pka"}
)
CHUNK_SIZE_BYTES = 1024 * 1024


class ChallengeFileStorageError(Exception):
    pass


class UnsupportedChallengeFileType(ChallengeFileStorageError):
    pass


class ChallengeFileTooLarge(ChallengeFileStorageError):
    pass


@dataclass(frozen=True)
class StoredChallengeFile:
    storage_provider: str
    storage_key: str
    original_filename: str
    display_name: str
    extension: str
    content_type: str | None
    size_bytes: int


def clean_original_filename(filename: str | None) -> str:
    cleaned = Path(filename or "challenge-file").name.strip()
    cleaned = "".join(char for char in cleaned if char.isprintable())
    return cleaned[:255] or "challenge-file"


def resolve_display_name(display_name: str | None, original_filename: str) -> str:
    chosen = " ".join((display_name or original_filename).strip().split())
    return chosen[:255] or original_filename


def extension_for(filename: str) -> str:
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_CHALLENGE_FILE_EXTENSIONS:
        raise UnsupportedChallengeFileType(extension or "(none)")
    return extension


class LocalChallengeFileStorage:
    provider = "local"

    def __init__(self, root: str | os.PathLike[str] | None = None, max_bytes: int | None = None):
        self.root = Path(root or settings.challenge_file_storage_root).resolve()
        self.max_bytes = max_bytes or settings.challenge_file_max_bytes

    def _path_for(self, storage_key: str) -> Path:
        path = (self.root / storage_key).resolve()
        if self.root not in path.parents:
            raise ChallengeFileStorageError("Storage key resolves outside storage root.")
        return path

    async def save(
        self,
        upload: UploadFile,
        *,
        challenge_id: UUID,
        display_name: str | None = None,
    ) -> StoredChallengeFile:
        original_filename = clean_original_filename(upload.filename)
        extension = extension_for(original_filename)
        file_id = uuid.uuid4()
        storage_key = f"challenges/{challenge_id}/files/{file_id}{extension}"
        destination = self._path_for(storage_key)
        destination.parent.mkdir(parents=True, exist_ok=True)

        size_bytes = 0
        try:
            with destination.open("wb") as target:
                while chunk := await upload.read(CHUNK_SIZE_BYTES):
                    size_bytes += len(chunk)
                    if size_bytes > self.max_bytes:
                        raise ChallengeFileTooLarge(str(self.max_bytes))
                    target.write(chunk)
        except Exception:
            destination.unlink(missing_ok=True)
            raise
        finally:
            await upload.close()

        return StoredChallengeFile(
            storage_provider=self.provider,
            storage_key=storage_key,
            original_filename=original_filename,
            display_name=resolve_display_name(display_name, original_filename),
            extension=extension,
            content_type=upload.content_type,
            size_bytes=size_bytes,
        )

    def path_for_download(self, storage_key: str) -> Path:
        path = self._path_for(storage_key)
        if not path.is_file():
            raise FileNotFoundError(storage_key)
        return path

    def delete(self, storage_key: str) -> None:
        self._path_for(storage_key).unlink(missing_ok=True)


def get_challenge_file_storage() -> LocalChallengeFileStorage:
    if settings.challenge_file_storage_provider != "local":
        raise ChallengeFileStorageError(
            f"Unsupported challenge file storage provider: {settings.challenge_file_storage_provider}"
        )
    return LocalChallengeFileStorage()
