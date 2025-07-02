from typing import Optional

from botocore.client import BaseClient
from fastapi import Depends, UploadFile

from app.core.dependencies import get_s3_client
from app.core.integrations.storage.base import BaseS3Storage


class CardS3DataManager(BaseS3Storage):
    """
    Менеджер для работы с S3 хранилищем.
    Расширяет базовый класс для специфических нужд приложения.
    """

    def __init__(self, s3_client: BaseClient):
        super().__init__(s3_client)

    async def process_card_image(
        self,
        old_image_url: str,
        file: UploadFile,
        file_content: Optional[bytes] = None,
    ) -> str:
        """
        Процессинг изображения: удаление старого и загрузка нового

        Args:
            old_image_url (str): URL старого изображения (если есть)
            file (UploadFile): Новое изображение для загрузки
            file_content (Optional[bytes], optional): Байтовое представление изображения (если есть). Defaults to None.
        """
        if (
            old_image_url
            and self.endpoint in old_image_url
            and self.bucket_name in old_image_url
        ):
            try:
                parts = old_image_url.split(f"{self.endpoint}/{self.bucket_name}/")
                if len(parts) > 1:
                    file_key = parts[1]
                    if await self.file_exists(file_key):
                        self.logger.info(
                            "Удаление старого изображения карточки: %s", file_key
                        )
                        await self.delete_file(file_key)
            except Exception as e:
                self.logger.error(
                    "Ошибка удаления старого изображения карточки: %s", str(e)
                )

        try:
            result = await self.upload_file_from_content(
                file=file, file_content=file_content, file_key="card_images"
            )
            self.logger.info("Загружено новое изображение карточки: %s", result)
            return result
        except Exception as e:
            self.logger.error("Ошибка загрузки нового изображения карточки: %s", str(e))
            raise ValueError("Не удалось загрузить файл изображения: %s", str(e))


async def get_card_s3_manager(
    s3_client=Depends(get_s3_client),
) -> CardS3DataManager:
    return CardS3DataManager(s3_client)
