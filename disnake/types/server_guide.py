# SPDX-License-Identifier: MIT

from typing import List, Literal, TypedDict

from typing_extensions import NotRequired

from .emoji import Emoji
from .snowflake import Snowflake, SnowflakeList

MemberActionActionType = Literal[0, 1]


class MemberAction(TypedDict):
    action_type: MemberActionActionType
    channel_id: Snowflake
    description: str
    title: str
    emoji: NotRequired[Emoji]


class ResourceChannel(TypedDict):
    channel_id: Snowflake
    title: str
    emoji: NotRequired[Emoji]


class WelcomeMessage(TypedDict):
    author_ids: SnowflakeList
    message: str


class ServerGuide(TypedDict):
    guild_id: Snowflake
    enabled: bool
    new_member_actions: List[MemberAction]
    resource_channels: List[ResourceChannel]
    welcome_message: WelcomeMessage
