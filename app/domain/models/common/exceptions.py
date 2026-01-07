class SenderIDCannotBeEmptyError(Exception):
    pass


class RecipientIDCannotBeEmptyError(Exception):
    pass


class ChatIDCannotBeEmptyError(Exception):
    pass


class MessageTextCannotBeEmptyError(Exception):
    pass


class CannotSendMessageToYourselfError(Exception):
    pass


class CannotReadDeletedMessageError(Exception):
    pass


class CannotEditDeletedMessageError(Exception):
    pass


class NewTextCannotBeEmptyError(Exception):
    pass


class MessageIsTooLongError(Exception):
    pass


class DeletedMessageCannotBeMarkedAsReadError(Exception):
    pass
