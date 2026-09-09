from abc import ABC


class Service(ABC):
    def __init__(self, *args, **kwargs) -> None: 
        super().__init__(*args, **kwargs)
