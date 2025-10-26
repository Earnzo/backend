import json
from channels.generic.websocket import AsyncWebsocketConsumer

class WalletConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if self.user.is_authenticated:
            # Create a unique group for this user's wallet updates
            self.wallet_group_name = f'wallet_{self.user.id}'
            
            # Join wallet group
            await self.channel_layer.group_add(
                self.wallet_group_name,
                self.channel_name
            )
            
            await self.accept()
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'user') and self.user.is_authenticated:
            # Leave wallet group
            await self.channel_layer.group_discard(
                self.wallet_group_name,
                self.channel_name
            )
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', '')
        
        if message_type == 'ping':
            await self.send(text_data=json.dumps({
                'type': 'pong'
            }))
    
    # Receive message from wallet group
    async def wallet_update(self, event):
        """Send wallet update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'wallet_update',
            'balance': str(event['balance']),
            'pending_balance': str(event['pending_balance']),
            'message': event['message']
        }))
