from __future__ import annotations

"""Welcome message configuration and verification helpers."""

from typing import Optional

import discord
from sqlalchemy import BigInteger, Column, String
from sqlalchemy.orm import Session

from .db import Base


class WelcomeConfig(Base):
    __tablename__ = "welcome_configs"

    guild_id = Column(BigInteger, primary_key=True)
    channel_id = Column(BigInteger, nullable=False)
    message = Column(String, nullable=False)
    verify_role_id = Column(BigInteger, nullable=True)


def get_config(db: Session, guild_id: int) -> Optional[WelcomeConfig]:
    return db.query(WelcomeConfig).filter_by(guild_id=guild_id).one_or_none()


def set_config(
    db: Session,
    guild_id: int,
    channel_id: int,
    message: str,
    verify_role_id: int | None,
) -> None:
    cfg = get_config(db, guild_id)
    if cfg:
        cfg.channel_id = channel_id
        cfg.message = message
        cfg.verify_role_id = verify_role_id
    else:
        cfg = WelcomeConfig(
            guild_id=guild_id,
            channel_id=channel_id,
            message=message,
            verify_role_id=verify_role_id,
        )
        db.add(cfg)
    db.commit()


class VerifyView(discord.ui.View):
    """Button view granting a role upon verification."""

    def __init__(self, role_id: int):
        super().__init__(timeout=None)
        self.role_id = role_id

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.primary)
    async def verify(  # type: ignore[override]
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        if not interaction.guild:
            await interaction.response.send_message("Guild only", ephemeral=True)
            return
        role = interaction.guild.get_role(self.role_id)
        member = interaction.guild.get_member(interaction.user.id)
        if role and member:
            await member.add_roles(role)
            await interaction.response.send_message("Verified", ephemeral=True)
        else:
            await interaction.response.send_message(
                "Verification failed", ephemeral=True
            )
