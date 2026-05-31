import discord
from pydantic import BaseModel, Field
from typing import Union, Optional, List, Dict
from ..base import BaseTool

class EmbedField(BaseModel):
    name: str
    value: str
    inline: bool = True

class SendEmbedMessageParams(BaseModel):
    channel_name_or_id: Union[str, int] = Field(..., description="The name or ID of the channel to send the embed to.")
    title: Optional[str] = Field(None, description="The title of the embed.")
    description: Optional[str] = Field(None, description="The main content/description of the embed.")
    color: Optional[str] = Field(None, description="Hex color code for the embed, e.g., '#00FF00'.")
    fields: List[EmbedField] = Field(default_factory=list, description="List of fields to add to the embed.")
    footer_text: Optional[str] = Field(None, description="Text for the footer.")
    thumbnail_url: Optional[str] = Field(None, description="URL for the thumbnail image.")
    image_url: Optional[str] = Field(None, description="URL for the large main image.")

class SendEmbedMessageTool(BaseTool):
    name = "send_embed_message"
    description = "Sends a rich, formatted embed message to a specific channel."
    schema = SendEmbedMessageParams

    async def execute(self, params: SendEmbedMessageParams, guild: discord.Guild):
        channel = None
        if isinstance(params.channel_name_or_id, int):
            channel = guild.get_channel(params.channel_name_or_id)
        else:
            channel = discord.utils.get(guild.text_channels, name=params.channel_name_or_id)

        if not channel or not isinstance(channel, discord.TextChannel):
            return {"error": f"Text channel '{params.channel_name_or_id}' not found."}

        color = discord.Color(int(params.color.lstrip("#"), 16)) if params.color else discord.Color.blue()
        
        embed = discord.Embed(
            title=params.title,
            description=params.description,
            color=color
        )

        for field in params.fields:
            embed.add_field(name=field.name, value=field.value, inline=field.inline)

        if params.footer_text:
            embed.set_footer(text=params.footer_text)
        
        if params.thumbnail_url:
            embed.set_thumbnail(url=params.thumbnail_url)
        
        if params.image_url:
            embed.set_image(url=params.image_url)

        try:
            message = await channel.send(embed=embed)
            return {"status": "success", "message_id": message.id}
        except discord.Forbidden:
            return {"error": "Bot does not have permission to send embeds in this channel."}
        except Exception as e:
            return {"error": str(e)}
