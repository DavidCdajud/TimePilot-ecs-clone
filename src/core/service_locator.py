class ServiceLocator:
    _services: dict[str, object] = {}

    @classmethod
    def register(cls, name: str, service: object) -> None:
        cls._services[name] = service

    @classmethod
    def get(cls, name: str) -> object:
        return cls._services[name]
