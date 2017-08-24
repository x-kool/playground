import enum

class CrawlerEnum(enum.Enum):
    @classmethod
    def get_enum_labels(cls):
        return [i.value for i in cls]

    @classmethod
    def get_name(cls):
        return cls.__name__