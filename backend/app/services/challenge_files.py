import os
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote
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


def download_content_disposition(filename: str) -> str:
    fallback = "".join(
        char if char.isascii() and char.isprintable() and char not in {'"', "\\", ";"} else "_"
        for char in filename
    ).strip(" .")
    fallback = fallback[:120] or "challenge-file"
    return f"attachment; filename=\"{fallback}\"; filename*=UTF-8''{quote(filename, safe='')}"


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

    def exists(self, storage_key: str) -> bool:
        return self._path_for(storage_key).is_file()

    def delete(self, storage_key: str) -> None:
        self._path_for(storage_key).unlink(missing_ok=True)


class S3ChallengeFileStorage:
    provider = "s3"

    def __init__(self, bucket: str | None = None, prefix: str | None = None, max_bytes: int | None = None):
        self.bucket = bucket or settings.challenge_file_s3_bucket
        if not self.bucket:
            raise ChallengeFileStorageError("S3 bucket is not configured.")
        self.prefix = (prefix if prefix is not None else settings.challenge_file_s3_prefix).strip("/")
        self.max_bytes = max_bytes or settings.challenge_file_max_bytes

    def _client(self):
        try:
            import boto3
        except ImportError as exc:
            raise ChallengeFileStorageError("boto3 is required for S3 challenge storage.") from exc
        return boto3.client("s3")

    def _key_for(self, challenge_id: UUID, file_id: uuid.UUID, extension: str) -> str:
        key = f"challenges/{challenge_id}/files/{file_id}{extension}"
        return f"{self.prefix}/{key}" if self.prefix else key

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
        storage_key = self._key_for(challenge_id, file_id, extension)
        size_bytes = 0

        with tempfile.SpooledTemporaryFile(max_size=CHUNK_SIZE_BYTES * 4) as temporary_file:
            try:
                while chunk := await upload.read(CHUNK_SIZE_BYTES):
                    size_bytes += len(chunk)
                    if size_bytes > self.max_bytes:
                        raise ChallengeFileTooLarge(str(self.max_bytes))
                    temporary_file.write(chunk)
                temporary_file.seek(0)
                self._client().upload_fileobj(
                    temporary_file,
                    self.bucket,
                    storage_key,
                    ExtraArgs={"ContentType": upload.content_type or "application/octet-stream"},
                )
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

    def presigned_download_url(self, storage_key: str, filename: str) -> str:
        return self._client().generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self.bucket,
                "Key": storage_key,
                "ResponseContentDisposition": download_content_disposition(filename),
            },
            ExpiresIn=settings.challenge_file_s3_presign_seconds,
        )

    def exists(self, storage_key: str) -> bool:
        try:
            self._client().head_object(Bucket=self.bucket, Key=storage_key)
            return True
        except Exception as exc:
            error_code = getattr(exc, "response", {}).get("Error", {}).get("Code")
            if error_code in {"404", "NoSuchKey", "NotFound"}:
                return False
            raise ChallengeFileStorageError("Unable to verify S3 challenge file.") from exc

    def delete(self, storage_key: str) -> None:
        self._client().delete_object(Bucket=self.bucket, Key=storage_key)


ChallengeFileStorage = LocalChallengeFileStorage | S3ChallengeFileStorage


def get_challenge_file_storage(provider: str | None = None) -> ChallengeFileStorage:
    provider_name = (provider or settings.challenge_file_storage_provider).lower()
    if provider_name == "local":
        return LocalChallengeFileStorage()
    if provider_name == "s3":
        return S3ChallengeFileStorage()
    raise ChallengeFileStorageError(
        f"Unsupported challenge file storage provider: {provider_name}"
    )
