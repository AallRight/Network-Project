import json

class Model:
    def __init__(self, cur_version=1):
        self.cur_version: int = cur_version
        self.data: list[int] = []
        self.pending_changes: dict[int, str] = {}

    def manipulate(self, change: str, based_on_version: int) -> dict[int, str]:
        applied_changes = {}

        if based_on_version == self.cur_version:
            applied = self.__apply(change)
            if applied:
                applied_changes = self.__update_version()
                applied_changes[based_on_version] = change
        elif based_on_version > self.cur_version:
            if based_on_version not in self.pending_changes:
                self.pending_changes[based_on_version] = change
            else:
                pass # discard this change
        else:
            pass # discard this change

        return {key: applied_changes[key] for key in sorted(applied_changes)}

    def __apply(self, change: str) -> bool:
        parts = change.split()
        if parts[0] == "push":
            if len(parts) != 2:
                return False
            try:
                value = int(parts[1])
                self.data.append(value)
            except ValueError:
                return False
        elif parts[0] == "pop":
            if len(parts) != 1:
                return False
            if len(self.data) == 0:
                return True
            self.data.pop()
        else:
            return False
        
        return True
    
    def __update_version(self) -> dict[int, str]:
        applied_changes = {}

        self.cur_version += 1
        if self.cur_version in self.pending_changes:
            change = self.pending_changes[self.cur_version]
            based_on_version = self.cur_version
            del self.pending_changes[self.cur_version]

            applied = self.__apply(change)
            
            if applied:
                applied_changes = self.__update_version()
                applied_changes[based_on_version] = change

        return applied_changes


    def serialize(self):
        return json.dumps({
            'cur_version': self.cur_version,
            'data': self.data
        })
    
    
    @classmethod
    def deserialize(cls, json_str):
        try:
            data_dict = json.loads(json_str)
            cur_version = data_dict['cur_version']
            data = data_dict['data']
            
            if not isinstance(cur_version, int):
                raise ValueError("cur_version must be an integer.")
            if not isinstance(data, list):
                raise ValueError("data must be a list.")
            
            db_instance = cls(cur_version)
            db_instance.data = data
            return db_instance
        
        except json.JSONDecodeError:
            print("Error: Invalid JSON format.")
        except KeyError as e:
            print(f"Error: Missing key in JSON data: {e}.")
        except ValueError as e:
            print(f"Error: {e}.")
        return cls()  # return a empty model instance
    

    def get_cur_version(self):
        return self.cur_version
    

    def get_num_pending_changes(self):
        return len(self.pending_changes)


if __name__ == "__main__":
    # Example usage
    db = Model(cur_version=1)

    def log_manipulate(change, based_on_version):
        applied_changes = db.manipulate(change, based_on_version)
        print(f"applied: {applied_changes}")
        print(f"db = {db.serialize()}")
        print()

    log_manipulate("push 9", 1)
    log_manipulate("push 8", 2)
    log_manipulate("push 7", 5) # pending
    log_manipulate("push 6", 4) # pending
    log_manipulate("push 5", 3)
    log_manipulate("push 4", 5)  # won't take effect
    log_manipulate("wrong 3", 6)  # won't take effect
    log_manipulate("wrong 2", 7)  # pending, won't take effect
    log_manipulate("pop", 6)