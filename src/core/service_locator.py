from services.images_service import ImagesService
from services.texts_service import TextService

class ServiceLocator:
    images_service = ImagesService()
    texts_service = TextService()