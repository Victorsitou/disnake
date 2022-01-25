"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz
Copyright (c) 2021-present Disnake Development

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Dict, List, Optional, Tuple, Type, TypeVar, Union

from .enums import ButtonStyle, ComponentType, InputTextStyle, try_enum
from .partial_emoji import PartialEmoji, _EmojiTag
from .utils import MISSING, get_slots

if TYPE_CHECKING:
    from .emoji import Emoji
    from .types.components import (
        ActionRow as ActionRowPayload,
        ButtonComponent as ButtonComponentPayload,
        Component as ComponentPayload,
        InputText as InputTextPayload,
        Modal as ModalPayload,
        SelectMenu as SelectMenuPayload,
        SelectOption as SelectOptionPayload,
    )


__all__ = (
    "Component",
    "ActionRow",
    "Button",
    "SelectMenu",
    "SelectOption",
    "Modal",
    "InputText",
)

C = TypeVar("C", bound="Component")


class Component:
    """Represents a Discord Bot UI Kit Component.

    Currently, the only components supported by Discord are:

    - :class:`ActionRow`
    - :class:`Button`
    - :class:`SelectMenu`

    This class is abstract and cannot be instantiated.

    .. versionadded:: 2.0

    Attributes
    ------------
    type: :class:`ComponentType`
        The type of component.
    """

    __slots__: Tuple[str, ...] = ("type",)

    __repr_info__: ClassVar[Tuple[str, ...]]
    type: ComponentType

    def __repr__(self) -> str:
        attrs = " ".join(f"{key}={getattr(self, key)!r}" for key in self.__repr_info__)
        return f"<{self.__class__.__name__} {attrs}>"

    @classmethod
    def _raw_construct(cls: Type[C], **kwargs) -> C:
        self: C = cls.__new__(cls)
        for slot in get_slots(cls):
            try:
                value = kwargs[slot]
            except KeyError:
                pass
            else:
                setattr(self, slot, value)
        return self

    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError


class ActionRow(Component):
    """Represents an Action Row.

    This is a component that holds up to 5 children components in a row.

    This inherits from :class:`Component`.

    .. versionadded:: 2.0

    Attributes
    ------------
    type: :class:`ComponentType`
        The type of component.
    children: List[:class:`Component`]
        The children components that this holds, if any.
    """

    __slots__: Tuple[str, ...] = ("children",)

    __repr_info__: ClassVar[Tuple[str, ...]] = __slots__

    def __init__(self, data: ComponentPayload):
        self.type: ComponentType = try_enum(ComponentType, data["type"])
        self.children: List[Component] = [_component_factory(d) for d in data.get("components", [])]

    def to_dict(self) -> ActionRowPayload:
        return {
            "type": int(self.type),
            "components": [child.to_dict() for child in self.children],
        }  # type: ignore


class Button(Component):
    """Represents a button from the Discord Bot UI Kit.

    This inherits from :class:`Component`.

    .. note::

        The user constructible and usable type to create a button is :class:`disnake.ui.Button`
        not this one.

    .. versionadded:: 2.0

    Attributes
    -----------
    style: :class:`.ButtonStyle`
        The style of the button.
    custom_id: Optional[:class:`str`]
        The ID of the button that gets received during an interaction.
        If this button is for a URL, it does not have a custom ID.
    url: Optional[:class:`str`]
        The URL this button sends you to.
    disabled: :class:`bool`
        Whether the button is disabled or not.
    label: Optional[:class:`str`]
        The label of the button, if any.
    emoji: Optional[:class:`PartialEmoji`]
        The emoji of the button, if available.
    """

    __slots__: Tuple[str, ...] = (
        "style",
        "custom_id",
        "url",
        "disabled",
        "label",
        "emoji",
    )

    __repr_info__: ClassVar[Tuple[str, ...]] = __slots__

    def __init__(self, data: ButtonComponentPayload):
        self.type: ComponentType = try_enum(ComponentType, data["type"])
        self.style: ButtonStyle = try_enum(ButtonStyle, data["style"])
        self.custom_id: Optional[str] = data.get("custom_id")
        self.url: Optional[str] = data.get("url")
        self.disabled: bool = data.get("disabled", False)
        self.label: Optional[str] = data.get("label")
        self.emoji: Optional[PartialEmoji]
        try:
            self.emoji = PartialEmoji.from_dict(data["emoji"])
        except KeyError:
            self.emoji = None

    def to_dict(self) -> ButtonComponentPayload:
        payload = {
            "type": 2,
            "style": int(self.style),
            "label": self.label,
            "disabled": self.disabled,
        }
        if self.custom_id:
            payload["custom_id"] = self.custom_id

        if self.url:
            payload["url"] = self.url

        if self.emoji:
            payload["emoji"] = self.emoji.to_dict()

        return payload  # type: ignore


class SelectMenu(Component):
    """Represents a select menu from the Discord Bot UI Kit.

    A select menu is functionally the same as a dropdown, however
    on mobile it renders a bit differently.

    .. note::

        The user constructible and usable type to create a select menu is
        :class:`disnake.ui.Select` not this one.

    .. versionadded:: 2.0

    Attributes
    ------------
    custom_id: Optional[:class:`str`]
        The ID of the select menu that gets received during an interaction.
    placeholder: Optional[:class:`str`]
        The placeholder text that is shown if nothing is selected, if any.
    min_values: :class:`int`
        The minimum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    max_values: :class:`int`
        The maximum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    options: List[:class:`SelectOption`]
        A list of options that can be selected in this menu.
    disabled: :class:`bool`
        Whether the select is disabled or not.
    """

    __slots__: Tuple[str, ...] = (
        "custom_id",
        "placeholder",
        "min_values",
        "max_values",
        "options",
        "disabled",
    )

    __repr_info__: ClassVar[Tuple[str, ...]] = __slots__

    def __init__(self, data: SelectMenuPayload):
        self.type = ComponentType.select
        self.custom_id: str = data["custom_id"]
        self.placeholder: Optional[str] = data.get("placeholder")
        self.min_values: int = data.get("min_values", 1)
        self.max_values: int = data.get("max_values", 1)
        self.options: List[SelectOption] = [
            SelectOption.from_dict(option) for option in data.get("options", [])
        ]
        self.disabled: bool = data.get("disabled", False)

    def to_dict(self) -> SelectMenuPayload:
        payload: SelectMenuPayload = {
            "type": self.type.value,
            "custom_id": self.custom_id,
            "min_values": self.min_values,
            "max_values": self.max_values,
            "options": [op.to_dict() for op in self.options],
            "disabled": self.disabled,
        }

        if self.placeholder:
            payload["placeholder"] = self.placeholder

        return payload


class SelectOption:
    """Represents a select menu's option.

    These can be created by users.

    .. versionadded:: 2.0

    Attributes
    -----------
    label: :class:`str`
        The label of the option. This is displayed to users.
        Can only be up to 100 characters.
    value: :class:`str`
        The value of the option. This is not displayed to users.
        If not provided when constructed then it defaults to the
        label. Can only be up to 100 characters.
    description: Optional[:class:`str`]
        An additional description of the option, if any.
        Can only be up to 100 characters.
    emoji: Optional[Union[:class:`str`, :class:`Emoji`, :class:`PartialEmoji`]]
        The emoji of the option, if available.
    default: :class:`bool`
        Whether this option is selected by default.
    """

    __slots__: Tuple[str, ...] = (
        "label",
        "value",
        "description",
        "emoji",
        "default",
    )

    def __init__(
        self,
        *,
        label: str,
        value: str = MISSING,
        description: Optional[str] = None,
        emoji: Optional[Union[str, Emoji, PartialEmoji]] = None,
        default: bool = False,
    ) -> None:
        self.label = label
        self.value = label if value is MISSING else value
        self.description = description

        if emoji is not None:
            if isinstance(emoji, str):
                emoji = PartialEmoji.from_str(emoji)
            elif isinstance(emoji, _EmojiTag):
                emoji = emoji._to_partial()
            else:
                raise TypeError(
                    f"expected emoji to be str, Emoji, or PartialEmoji not {emoji.__class__}"
                )

        self.emoji = emoji
        self.default = default

    def __repr__(self) -> str:
        return (
            f"<SelectOption label={self.label!r} value={self.value!r} description={self.description!r} "
            f"emoji={self.emoji!r} default={self.default!r}>"
        )

    def __str__(self) -> str:
        if self.emoji:
            base = f"{self.emoji} {self.label}"
        else:
            base = self.label

        if self.description:
            return f"{base}\n{self.description}"
        return base

    @classmethod
    def from_dict(cls, data: SelectOptionPayload) -> SelectOption:
        try:
            emoji = PartialEmoji.from_dict(data["emoji"])
        except KeyError:
            emoji = None

        return cls(
            label=data["label"],
            value=data["value"],
            description=data.get("description"),
            emoji=emoji,
            default=data.get("default", False),
        )

    def to_dict(self) -> SelectOptionPayload:
        payload: SelectOptionPayload = {
            "label": self.label,
            "value": self.value,
            "default": self.default,
        }

        if self.emoji:
            payload["emoji"] = self.emoji.to_dict()  # type: ignore

        if self.description:
            payload["description"] = self.description

        return payload


class InputText(Component):
    """Represents an input text from the Discord Bot UI Kit.

    This can only be used in a :class:`~.ui.Modal`.

    .. versionadded:: 2.4

    .. note::

        The user constructible and usable type to create an input text is
        :class:`disnake.ui.InputText`, not this one.

    Attributes
    -----------
    style: :class:`InputTextStyle`
        The style of the input text.
    label: Optional[:class:`str`]
        The label of the input text.
    custom_id: :class:`str`
        The ID of the input text that gets received during an interaction.
    placeholder: Optional[:class:`str`]
        The placeholder text that is shown if nothing is entered.
    value: Optional[:class:`str`]
        The pre-filled text of the input text.
    required: :class:`bool`
        Whether the input text is required. Defaults to ``True``.
    min_length: :class:`int`
        The minimum length of the input text. Defaults to ``0``.
    max_length: Optional[:class:`int`]
        The maximum length of the input text.
    """

    __slots__: Tuple[str, ...] = (
        "style",
        "custom_id",
        "label",
        "placeholder",
        "value",
        "required",
        "max_length",
        "min_length",
    )

    __repr_info__: ClassVar[Tuple[str, ...]] = __slots__

    def __init__(self, data: InputTextPayload) -> None:
        style = data.get("style", InputTextStyle.short.value)

        self.type: ComponentType = try_enum(ComponentType, data["type"])
        self.custom_id: str = data["custom_id"]
        self.style: InputTextStyle = try_enum(InputTextStyle, style)
        self.label: Optional[str] = data.get("label")
        self.placeholder: Optional[str] = data.get("placeholder")
        self.value: Optional[str] = data.get("value")
        self.required: bool = data.get("required", True)
        self.min_length: int = data.get("min_length", 0)
        self.max_length: Optional[int] = data.get("max_length")

    def to_dict(self) -> InputTextPayload:
        payload: InputTextPayload = {
            "type": self.type.value,
            "style": self.style.value,  # type: ignore
            "label": self.label,
            "custom_id": self.custom_id,
            "required": self.required,
            "min_length": self.min_length,
        }

        if self.placeholder:
            payload["placeholder"] = self.placeholder

        if self.value:
            payload["value"] = self.value

        if self.max_length:
            payload["max_length"] = self.max_length

        return payload


class Modal:
    # Notice that this is not a component according to API docs.

    """Represents a modal.

    .. versionadded:: 2.4

    .. note::

        The user constructible and usable type to create a modal is
        :class:`disnake.ui.Modal`, not this one.

    Attributes
    ----------
    title: :class:`str`
        The title of the modal.
    custom_id: :class:`str`
        The ID of the modal that gets received during an interaction.
    components: List[:class:`~.ui.InputText`]
        The components the modal has.
    """

    __slots__: Tuple[str, ...] = ("title", "custom_id", "components")

    def __init__(self, data: ModalPayload) -> None:
        self.title: str = data["title"]
        self.custom_id: str = data["custom_id"]
        self.components: List[ActionRow] = [ActionRow(d) for d in data["components"]]
        # it's safe to assume that top-level components are action rows.
        # if Discord changes this (which is unlikely), they'll give us enough time to adapt.

    def __repr__(self) -> str:
        return (
            f"<Modal custom_id={self.custom_id!r} title={self.title!r} "
            f"components={self.components!r}>"
        )

    def to_dict(self) -> ModalPayload:
        payload: ModalPayload = {
            "title": self.title,
            "custom_id": self.custom_id,
            "components": [component.to_dict() for component in self.components],
        }

        return payload

    @classmethod
    def from_attributes(
        cls, *, title: str, custom_id: str, components: List[ActionRow] = None
    ) -> Modal:
        self = cls.__new__(cls)
        self.title = title
        self.custom_id = custom_id
        self.components = components or []
        return self


def _component_factory(data: ComponentPayload) -> Component:
    component_type = data["type"]
    if component_type == 1:
        return ActionRow(data)
    elif component_type == 2:
        return Button(data)  # type: ignore
    elif component_type == 3:
        return SelectMenu(data)  # type: ignore
    elif component_type == 4:
        return InputText(data)  # type: ignore
    else:
        as_enum = try_enum(ComponentType, component_type)
        return Component._raw_construct(type=as_enum)
