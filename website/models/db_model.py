from typing import Dict


class DBModel:
    def cast_to_document(self) -> Dict[str, object]:
        pass

    def save(self, replace=False, wait=False):
        pass

    def delete(self, wait=False):
        pass
