from dataclasses import dataclass
from LuminMessageService.app.domain.models.common.exceptions import MessageIsTooLongError, MessageTextCannotBeEmptyError


@dataclass(frozen=True)
class MessageText:
    _text: str

    def __post_init__(self):
        if not self._text or not self._text.strip():
            raise MessageTextCannotBeEmptyError("Text cannot be empty")
        if len(self._text) > 5000:
            raise MessageIsTooLongError("Text is too long")

    @property
    def value(self) -> str:
        return self._text

    def __eq__(self, other):
        return isinstance(other, MessageText) and self._text == other._text
