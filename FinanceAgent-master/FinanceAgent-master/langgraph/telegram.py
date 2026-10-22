import os
from telethon import TelegramClient
from dotenv import load_dotenv
from typing import List, Dict, Optional
import asyncio
from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class TelegramFetcher:
    def __init__(self):
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.client = None
        
        if not self.api_id or not self.api_hash:
            raise ValueError("TELEGRAM_API_ID and TELEGRAM_API_HASH must be set in .env file")

    async def _get_channel_messages(self, channel_username: str, limit: int = 10) -> List[dict]:
        """Fetch messages from a specific Telegram channel."""
        try:
            channel = await self.client.get_entity(channel_username)
            messages = await self.client.get_messages(channel, limit=limit)
            
            formatted_messages = []
            for message in messages:
                formatted_messages.append({
                    'channel': channel_username,
                    'message_id': message.id,
                    'from': message.sender_id,
                    'date': message.date.strftime('%Y-%m-%d %H:%M:%S'),
                    'text': message.text
                })
            
            return formatted_messages
        except Exception as e:
            logger.error(f"Error fetching messages from {channel_username}: {e}")
            return []

    async def _get_messages_from_channels(self, channel_usernames: List[str], limit: int = 10) -> List[Dict]:
        """Fetch messages from multiple Telegram channels."""
        try:
            self.client = TelegramClient('session_name', self.api_id, self.api_hash)
            await self.client.start()
            
            all_messages = []
            for channel in channel_usernames:
                logger.info(f"Fetching messages from {channel}...")
                messages = await self._get_channel_messages(channel, limit)
                all_messages.extend(messages)
            
            # Sort all messages by date (newest first)
            all_messages.sort(key=lambda x: x['date'], reverse=True)
            return all_messages
                
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return []
        finally:
            if self.client:
                await self.client.disconnect()

    def get_messages(self, channels: List[str], limit: int = 10) -> str:
        """
        Get messages from specified Telegram channels and return them as JSON.
        
        Args:
            channels (List[str]): List of channel usernames (without @)
            limit (int): Number of latest messages to fetch from each channel
            
        Returns:
            str: JSON string containing the messages
        """
        try:
            messages = asyncio.run(self._get_messages_from_channels(channels, limit))
            return json.dumps(messages, indent=2)
        except Exception as e:
            logger.error(f"Error in get_messages: {e}")
            return json.dumps({"error": str(e)})

# For testing purposes
if __name__ == "__main__":
    channels = [
        "whale_alert",
        "bitexgroupsignal"
    ]
    
    fetcher = TelegramFetcher()
    result = fetcher.get_messages(channels)
    print(result)
