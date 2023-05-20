# SPDX-License-Identifier: MIT
from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Union

from .enums import MemberActionActionType, try_enum

if TYPE_CHECKING:
    from .emoji import Emoji, PartialEmoji
    from .guild import Guild, GuildMessageable
    from .member import Member
    from .types.server_guide import (
        MemberAction as MemberActionPayload,
        ResourceChannel as ResourceChannelPayload,
        ServerGuide as ServerGuidePayload,
        WelcomeMessage as WelcomeMessagePayload,
    )

__all__ = (
    "ServerGuide",
    "MemberAction",
    "ResourceChannel",
    "WelcomeMessage",
)


class ServerGuide:
    """Represents a Discord Server Guide for a :class:`Guild`.

    .. versionadded:: 2.?

    Attributes
    ----------
    guild: :class:`Guild`
        The guild this server guide belongs to.
    enabled: :class:`bool`
        Whether this server guide is enabled.
    new_member_actions: List[:class:`MemberAction`]
        The list of new member actions.
    resource_channels: List[:class:`ResourceChannel`]
        The list of resource channels.
    welcome_message: :class:`WelcomeMessage`
        The welcome message.
    """

    __slots__ = ("guild", "enabled", "new_member_actions", "resource_channels", "welcome_message")

    def __init__(self, guild: Guild, data: ServerGuidePayload):
        self.guild = guild
        self.enabled: bool = data["enabled"]
        # TODO: convert
        # TODO: frozenset?
        self.new_member_actions: List[MemberAction] = [
            MemberAction(guild, action) for action in data["new_member_actions"]
        ]
        self.resource_channels: List[ResourceChannel] = [
            ResourceChannel(guild, channel) for channel in data["resource_channels"]
        ]
        self.welcome_message: WelcomeMessage = WelcomeMessage(guild, data["welcome_message"])

    def __repr__(self) -> str:
        return (
            f"<ServerGuide guild={self.guild!r} enabled={self.enabled} "
            f"new_member_actions={self.new_member_actions} resource_channels={self.resource_channels} "
            f"welcome_message={self.welcome_message}>"
        )


class MemberAction:
    """Represents an action a new member can do.

    .. versionadded:: 2.?

    Attributes
    ----------
    action_type: :class:`MemberActionActionType`
        The action type.
    channel_id: :class:`int`
        The ID of the channel this action is associated with.
    title: :class:`str`
        The title of this action.
    description: :class:`str`
        The description of this action.
    emoji: Optional[Union[:class:`PartialEmoji`, :class:`Emoji`, :class:`str`]]
        The emoji associated with this action.
    """

    __slots__ = ("guild", "action_type", "channel_id", "title", "description", "emoji")

    def __init__(self, guild: Guild, data: MemberActionPayload):
        self.guild: Guild = guild
        self.action_type: MemberActionActionType = try_enum(
            MemberActionActionType, data["action_type"]
        )
        self.channel_id: int = int(data["channel_id"])
        self.title: str = data["title"]
        # NOTE: this is always empty and you can't set it in client
        self.description: str = data["description"]

        self.emoji: Optional[Union[Emoji, PartialEmoji, str]]
        if emoji_data := data.get("emoji"):
            self.emoji = guild._state.get_reaction_emoji(emoji_data)
        else:
            self.emoji = None

    def __repr__(self) -> str:
        return (
            f"<MemberAction action_type={self.action_type} channel_id={self.channel_id} title={self.title!r} "
            f"description={self.description!r} emoji={self.emoji}>"
        )

    @property
    def channel(self) -> GuildMessageable:
        # TODO: define what type of channels this can return
        """Optional[:class:`GuildMessageable`]: The channel associated with this action."""
        return self.guild.get_channel(self.channel_id)  # type: ignore


class ResourceChannel:
    """Represents a resource channel in the guild's server guide.

    .. versionadded:: 2.?

    Attributes
    ----------
    channel_id: :class:`int`
        The ID of the channel.
    title: :class:`str`
        The title of this resource channel.
    emoji: Optional[Union[:class:`PartialEmoji`, :class:`Emoji`, :class:`str`]]
        The emoji associated with this resource channel.
    """

    __slots__ = ("guild", "channel_id", "title", "emoji")

    def __init__(self, guild: Guild, data: ResourceChannelPayload):
        self.guild: Guild = guild
        self.channel_id: int = int(data["channel_id"])
        self.title: str = data["title"]
        self.emoji: Optional[Union[Emoji, PartialEmoji, str]]
        if emoji_data := data.get("emoji"):
            self.emoji = guild._state.get_reaction_emoji(emoji_data)
        else:
            self.emoji = None

    def __repr__(self) -> str:
        return (
            f"<ResourceChannel channel_id={self.channel_id} "
            f"title={self.title!r} emoji={self.emoji}>"
        )

    @property
    def channel(self) -> GuildMessageable:
        # TODO: define what type of channels this can return
        """Optional[:class:`GuildMessageable`]: The channel associated with this action."""
        return self.guild.get_channel(self.channel_id)  # type: ignore


class WelcomeMessage:
    """Represents the welcome message in the guild's server guide.

    .. versionadded:: 2.?

    Attributes
    ----------
    author_ids: List[:class:`int`]
        The IDs of the authors of this welcome message.
    message: :class:`str`
        The welcome message.
    """

    def __init__(self, guild: Guild, data: WelcomeMessagePayload):
        self.guild: Guild = guild
        self.author_ids: List[int] = [int(author_id) for author_id in data["author_ids"]]
        self.message: str = data["message"]

    def __repr__(self) -> str:
        return f"<WelcomeMessage author_ids={self.author_ids} message={self.message!r}>"

    @property
    def authors(self) -> List[Member]:
        # NOTE: as of 05/20 this can only return one author since the client only allows one
        """List[:class:`Member`]: The authors of this welcome message."""
        return list(
            filter(None, (self.guild.get_member(author_id) for author_id in self.author_ids))
        )
