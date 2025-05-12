from services.images_service import ImagesService
from services.texts_service import TextService
from services.sound_service import SoundService

class ServiceLocator:
    images_service = ImagesService()
    texts_service = TextService()
    sound_service = SoundService()