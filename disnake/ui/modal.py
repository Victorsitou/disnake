"""
The MIT License (MIT)

Copyright (c) 2021-present DisnakeDev

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

import asyncio
import sys
import traceback
from typing import TYPE_CHECKING, Dict, List, Tuple, Union, overload

from ..components import (
    ActionRow as ActionRowComponent,
    InputText as InputTextComponent,
    Modal as ModalComponent,
)
from ..enums import ComponentType
from .action_row import components_to_rows
from .input_text import InputText

if TYPE_CHECKING:
    from ..interactions.modal import ModalInteraction
    from ..state import ConnectionState
    from ..types.components import Modal as ModalPayload
    from .action_row import Components


__all__ = ("Modal",)


class Modal:
    """Represents a UI Modal.

    .. versionadded:: 2.4

    Parameters
    ----------
    title: :class:`str`
        The title of the modal.
    custom_id: :class:`str`
        The custom ID of the modal.
    components: |components_type|
        The components to display in the modal. Up to 5 action rows.
    """

    __slots__ = ("_underlying",)

    def __init__(
        self,
        *,
        title: str,
        custom_id: str,
        components: Components,
    ) -> None:
        ui_action_rows = components_to_rows(components)
        action_rows = []

        for ui_row in ui_action_rows:
            if not all(isinstance(c, InputTextComponent) for c in ui_row.children):
                raise TypeError("Components must be of type InputText.")
            action_rows.append(ui_row._underlying)

        self._underlying = ModalComponent.from_attributes(
            title=title, custom_id=custom_id, components=action_rows
        )

    def __repr__(self) -> str:
        return repr(self._underlying)

    @property
    def title(self) -> str:
        """:class:`str`: The title of the modal."""
        return self._underlying.title

    @title.setter
    def title(self, title: str) -> None:
        self._underlying.title = title

    @property
    def custom_id(self) -> str:
        """:class:`str`: The ID of the modal that gets received during an interaction."""
        return self._underlying.custom_id

    @custom_id.setter
    def custom_id(self, custom_id: str) -> None:
        self._underlying.custom_id = custom_id

    @property
    def components(self) -> List[ActionRowComponent]:
        """List[:class:`~.ui.InputText`]: A list of components the modal contains."""
        return self._underlying.components

    @overload
    def add_component(self, component: List[InputText]) -> None:
        ...

    @overload
    def add_component(self, component: InputText) -> None:
        ...

    def add_component(self, component: Union[InputText, List[InputText]]) -> None:
        """Adds a component to the modal.

        Parameters
        ----------
        component: Union[:class:`~.ui.InputText`, List[:class:`~.ui.InputText`]]
            The component to add to the modal.
            This can be a single component or a list of components.

        Raises
        ------
        ValueError
            Maximum of components exceeded. (5)
        TypeError
            An :class:`InputText` object was not passed.
        """
        if len(self.components) == 5:
            raise ValueError("maximum of components exceeded.")

        if not isinstance(component, list):
            component = [component]

        for c in component:
            if not isinstance(c, InputText):
                raise TypeError(
                    f"component must be of type InputText or a list of InputText, not {c.__class__.__name__}."
                )
            new_row = ActionRowComponent._raw_construct(
                type=ComponentType.action_row,
                children=[c._underlying],
            )
            self._underlying.components.append(new_row)

    async def callback(self, interaction: ModalInteraction) -> None:
        """|coro|

        The callback associated with this modal.

        This can be overriden by subclasses.

        Parameters
        ----------
        interaction: :class:`.ModalInteraction`
            The interaction that triggered this modal.
        """
        pass

    async def on_error(self, error: Exception, interaction: ModalInteraction) -> None:
        """|coro|

        A callback that is called when an error occurs.

        The default implementation prints the traceback to stderr.

        Parameters
        ----------
        error: :class:`Exception`
            The exception that was raised.
        interaction: :class:`.ModalInteraction`
            The interaction that triggered this modal.
        """
        traceback.print_exception(error.__class__, error, error.__traceback__, file=sys.stderr)

    def to_components(self) -> ModalPayload:
        return self._underlying.to_dict()

    async def _scheduled_task(self, interaction: ModalInteraction) -> None:
        try:
            await self.callback(interaction)
        except Exception as e:
            await self.on_error(e, interaction)
        else:
            interaction._state._modal_store.remove_modal(
                interaction.author.id, interaction.custom_id
            )

    def dispatch(self, interaction: ModalInteraction) -> None:
        asyncio.create_task(
            self._scheduled_task(interaction), name=f"disnake-ui-modal-dispatch-{self.custom_id}"
        )


class ModalStore:
    def __init__(self, state: ConnectionState) -> None:
        self._state = state
        # (user_id, Modal.custom_id): Modal
        self._modals: Dict[Tuple[int, str], Modal] = {}

    def add_modal(self, user_id: int, modal: Modal) -> None:
        loop = asyncio.get_event_loop()
        self._modals[(user_id, modal.custom_id)] = modal
        loop.create_task(self.handle_timeout(user_id, modal.custom_id))

    def remove_modal(self, user_id: int, modal_custom_id: str) -> None:
        self._modals.pop((user_id, modal_custom_id))

    async def handle_timeout(self, user_id: int, modal_custom_id: str) -> None:
        # Waits 10 minutes and then removes the modal from cache, this is done just in case the user closed the modal,
        # as there isn't an event for that.

        await asyncio.sleep(600)
        try:
            self.remove_modal(user_id, modal_custom_id)
        except KeyError:
            # The modal has already been removed.
            pass

    def dispatch(self, interaction: ModalInteraction) -> None:
        key = (interaction.author.id, interaction.custom_id)
        modal = self._modals.get(key)
        if modal is not None:
            modal.dispatch(interaction)
