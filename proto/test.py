import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
sys.dont_write_bytecode = True

from proto.client_command_pb2 import ClientCommand
from google.protobuf.json_format import MessageToDict

def main():
    print("\n创建 ClientCommand")
    command = ClientCommand()
    command.command_id = 42
    command.user_id = 24
    waitlist_move = command.waitlist_move
    waitlist_move.wid = 10
    waitlist_move.offset = -3
    print(command)
    
    print("\n序列化")
    serialized_command = command.SerializeToString()
    print(f"十六进制：0x{serialized_command.hex()}，长度：{len(serialized_command)}")
    
    print("\n反序列化")
    new_command = ClientCommand()
    new_command.ParseFromString(serialized_command)
    print(new_command)
    
    print("\n启用了 oneof 的哪一个字段")
    print(new_command.WhichOneof("command"))

if __name__ == "__main__":
    main()