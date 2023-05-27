# SPDX-License-Identifier: MIT

from typing import List
from unittest import mock

import pytest

from disnake import Guild, MemberAction, ResourceChannel, ServerGuide, WelcomeMessage
from disnake.types import server_guide as server_guide_types


@pytest.fixture
def server_guide() -> ServerGuide:
    return ServerGuide(
        guild=mock.Mock(Guild, id=123),
        data=server_guide_types.ServerGuide(
            guild_id="123",
            enabled=True,
            new_member_actions=[
                {
                    "action_type": 0,
                    "channel_id": "123",
                    "description": "desc",
                    "title": "title",
                },
                {
                    "action_type": 1,
                    "channel_id": "123",
                    "description": "desc2",
                    "title": "title2",
                    "emoji": {"name": "", "id": "345", "animated": False},
                },
            ],
            resource_channels=[
                {
                    "channel_id": "456",
                    "title": "title",
                },
                {
                    "channel_id": "789",
                    "title": "title2",
                    "emoji": {"name": "", "id": "321", "animated": False},
                },
            ],
            welcome_message={
                "author_ids": ["123"],
                "message": "welcome!",
            },
        ),
    )


@pytest.fixture
def member_actions() -> List[MemberAction]:
    return [
        MemberAction(
            guild=mock.Mock(Guild, id=123),
            data=server_guide_types.MemberAction(
                action_type=0, channel_id="123", description="desc", title="title"
            ),
        ),
        MemberAction(
            guild=mock.Mock(Guild, id=123),
            data=server_guide_types.MemberAction(
                action_type=1,
                channel_id="123",
                description="desc2",
                title="title2",
                emoji={"name": "", "id": "345", "animated": False},
            ),
        ),
    ]


@pytest.fixture
def resource_channels() -> List[ResourceChannel]:
    return [
        ResourceChannel(
            guild=mock.Mock(Guild, id=123),
            data=server_guide_types.ResourceChannel(
                channel_id="456",
                title="title",
            ),
        ),
        ResourceChannel(
            guild=mock.Mock(Guild, id=123),
            data=server_guide_types.ResourceChannel(
                channel_id="789",
                title="title2",
                emoji={"name": "", "id": "321", "animated": False},
            ),
        ),
    ]


@pytest.fixture
def welcome_message() -> WelcomeMessage:
    return WelcomeMessage(
        guild=mock.Mock(Guild, id=123),
        data=server_guide_types.WelcomeMessage(
            author_ids=["123"],
            message="welcome!",
        ),
    )


class TestServerGuide:
    def test_server_guide(
        self,
        server_guide: ServerGuide,
        member_actions: List[MemberAction],
        resource_channels: List[ResourceChannel],
        welcome_message: WelcomeMessage,
    ) -> None:
        assert server_guide.guild.id == 123
        assert server_guide.enabled is True

        for one, two in zip(server_guide.new_member_actions, member_actions):
            assert one.action_type == two.action_type
            assert one.channel_id == two.channel_id
            assert one.description == two.description
            assert one.title == two.title

        for one, two in zip(server_guide.resource_channels, resource_channels):
            assert one.channel_id == two.channel_id
            assert one.title == two.title

        assert server_guide.welcome_message.author_ids == welcome_message.author_ids
        assert server_guide.welcome_message.message == welcome_message.message
