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
                except Exception as e:
                    raise NotImplementedError(f"{operation} is not implemented.") from e
            else:
                handler = globals().get(operation)
                if handler is not callable:
                    raise NotImplementedError(f"{operation} is not implemented.")
            self.operation_handlers[operation] = handler
            self.operation_params[operation] = [p.name for p in signature(handler).parameters.values()]
    
    def handle(self, message):
        operation = message.WhichOneof(self.oneof_field)
        try:
            args = getattr(message, operation)
        except Exception as e:
            raise Exception(f"Missing operation. (message: >>> {message} <<<)") from e
        handler = self.operation_handlers[operation]
        params = self.operation_params[operation]
        try:
            kwargs = {param: getattr(args, param) for param in params}
        except Exception as e:
            raise Exception(f"Missing arg. (got {args}, excepted {params})") from e
        return handler(**kwargs)
    
    async def async_handle(self, message):
        operation = message.WhichOneof(self.oneof_field)
        try:
            args = getattr(message, operation)
        except Exception as e:
            raise Exception(f"Missing operation. (message: >>> {message} <<<)") from e
        handler = self.operation_handlers[operation]
        params = self.operation_params[operation]
        try:
            kwargs = {param: getattr(args, param) for param in params}
        except Exception as e:
            raise Exception(f"Missing arg. (got {args}, excepted {params})") from e
        return await handler(**kwargs)