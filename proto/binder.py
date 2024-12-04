from inspect import signature

class HandlerBinder:
    def __init__(self, message_type, oneof_field: str, obj=None):
        self.oneof_field = oneof_field
        operations = [field.name for field in message_type.DESCRIPTOR.oneofs_by_name[oneof_field].fields]
        self.operation_handlers, self.operation_params = {}, {}
        for operation in operations:
            if obj is not None:
                try:
                    handler = getattr(obj, operation)
                except AttributeError:
                    raise NotImplementedError(f"{operation} is not implemented.")
            else:
                handler = globals().get(operation)
                if handler is not callable:
                    raise NotImplementedError(f"{operation} is not implemented.")
            self.operation_handlers[operation] = handler
            self.operation_params[operation] = [p.name for p in signature(handler).parameters.values()]
    
    def handle(self, message):
        operation = message.WhichOneof(self.oneof_field)
        args = getattr(message, operation)
        handler = self.operation_handlers[operation]
        params = self.operation_params[operation]
        kwargs = {param: getattr(args, param) for param in params}
        return handler(**kwargs)