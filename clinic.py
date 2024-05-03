from ordered_set import OrderedSet


class Clinic:
    name: str
    url: str
    doctors: OrderedSet

    def __init__(self, name: str = "", url: str = "", doctors=None):
        if doctors is None:
            doctors = OrderedSet()
        self._name = name
        self._url = url
        self._doctors = doctors

    @property
    def get_name(self) -> str:
        return self._name

    @property
    def get_url(self) -> str:
        return self._url

    def set_name(self, _name):
        self._name = _name

    def set_url(self, _url):
        self._url = _url

    @property
    def get_doctors(self) -> OrderedSet:
        return self._doctors

    def __str__(self):
        return self._name.strip()

