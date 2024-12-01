from maindata.api import MainData

class Command:
    pass

class Model:
    def __init__(self, db_path: str, music_path: str):
        self.maindata = MainData(db_path, music_path)
    

    def execute(command: str):
        pass