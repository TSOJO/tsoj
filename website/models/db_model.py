from typing import Dict


class DBModel:
    def cast_to_document(self) -> Dict[str, object]:
        pass

    def save(self):
        pass

    def delete(self):
        pass