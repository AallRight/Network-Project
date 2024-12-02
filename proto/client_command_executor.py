from inspect import signature
from proto.client_command_pb2 import ClientCommand

class ClientCommandExecutor:
    """
    ClientCommandExecutor class is responsible for executing client commands.
    
    It associates commands with their corresponding handlers and triggers the appropriate handler based on the provided ClientCommand object.
    """
    def __init__(self, obj=None):
        """
        Initialize the ClientCommandExecutor instance.
        
        :param obj: Optional parameter, an object containing methods to handle commands.
                    If None, it will look for handlers in the global scope.
        """
        commands = [field.name for field in ClientCommand.DESCRIPTOR.oneofs_by_name["command"].fields]
        self.command_handlers, self.command_handlers_params = {}, {}
        for command in commands:
            if obj is not None:
                try:
                    handler = getattr(obj, command)
                except AttributeError:
                    raise NotImplementedError(f"{command} is not implemented.")
            else:
                handler = globals().get(command)
                if handler is not callable:
                    raise NotImplementedError(f"{command} is not implemented.")
            self.command_handlers[command] = handler
            self.command_handlers_params[command] = [p.name for p in signature(handler).parameters.values()]
    
    def execute(self, client_command: ClientCommand):
        """
        Execute the given client command.
        
        :param client_command: Instance of ClientCommand containing the command to execute and its parameters.
        """
        command = client_command.WhichOneof("command")
        args = getattr(client_command, command)
        handler = self.command_handlers[command]
        params = self.command_handlers_params[command]
        kwargs = {param: getattr(args, param) for param in params}
        return handler(**kwargs)