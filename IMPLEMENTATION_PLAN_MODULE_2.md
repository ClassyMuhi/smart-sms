# Implementation Plan: Messaging Core (REST + WebSocket)

This plan outlines the steps to build the messaging core, handling reliable message storage, real-time delivery via WebSockets, and fallback delivery mechanisms.

## Technology Stack Additions
- **Django Channels**: For handling WebSocket connections within Django.
- **Daphne**: An ASGI server to serve both HTTP and WebSocket traffic.
- **Redis & Channels Redis Layer**: To enable inter-process communication so that messages can be broadcasted across different WebSocket connections securely.

## Phase 1: Setup & Configuration
1. **Install Dependencies**:
   ```bash
   pip install channels daphne channels-redis
   ```
2. **Update `settings.py`**:
   - Add `daphne` and `channels` to `INSTALLED_APPS` (ensure `daphne` is at the very top).
   - Change `WSGI_APPLICATION` to `ASGI_APPLICATION = "smartsms.asgi.application"`.
   - Configure the `CHANNEL_LAYERS` setting to use Redis as the backend.

## Phase 2: Database Schema (Models)
Create a new Django app (e.g., `messaging`) and add the model:
```python
class Message(models.Model):
    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    )
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    conversation_id = models.CharField(max_length=255, db_index=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')

    class Meta:
        ordering = ['timestamp']
```
*Action*: Create and apply migrations.

## Phase 3: REST API Endpoints
1. **POST `/api/messages/send`**:
   - Validates sender (via JWT).
   - Validates receiver existence.
   - Saves message to DB (`status='sent'`).
   - *Async Hook*: Triggers a Channel Layer broadcast to the receiver's personal WebSocket group.
   - Returns the created `message_id`.

2. **GET `/api/messages/{conversation_id}`**:
   - Requires JWT authentication.
   - Fetches paginated history of messages for the exact conversation.

## Phase 4: WebSocket Layer (Real-Time)
1. **Authentication Middleware (`middleware.py`)**:
   - Build a custom ASGI middleware to parse the JWT from the `?token=JWT` in ASGI scope. This extracts the authenticated user.
   
2. **Chat Consumer (`consumers.py`)**:
   - **`connect`**: Validates JWT. Adds user to a group mapped to their ID (e.g., `user_personal_<user_id>`). Accepts connection.
   - **`disconnect`**: Removes user from the personal group.
   - **`receive` (from client)**: 
     - Parses JSON payload `{receiver_id, content}`.
     - Saves message to DB.
     - Attempts broadcasting to `user_personal_<receiver_id>`.
     - Sends `delivery_update` `{message_id, status: sent/delivered}` back to sender.
   - **`receive_message` (from channel layer)**: Send the incoming payload down to the connected WebSocket client.

3. **Routing (`routing.py`)**:
   - Map WebSocket URL `/ws/chat/<user_id>?token=...` to the `ChatConsumer`.

4. **Update `asgi.py`**:
   - Wrap application with `ProtocolTypeRouter`, using `URLRouter` for WebSockets and the custom JWT Auth middleware.

## Phase 5: Core Delivery Logic Lifecycle
- **Step 1**: User A hits REST API or WebSocket to send message to User B.
- **Step 2**: Message saved to Database (Status: `Sent`).
- **Step 3**: Server performs a channel layer `group_send` to User B's group `user_personal_B`.
- **Step 4**: 
  - *Scenario Online*: User B's WebSocket receives the dispatch. Converts it to JSON and sends it over to B. User B's client acknowledges receipt. DB updates Status to `Delivered`.
  - *Scenario Offline*: Message waits in DB. Unchanged status. Next time User B connects, their client queries REST GET for missed messages.

## Phase 6: Testing & Validation
- Check ASGI routing configuration.
- Write tests simulating dual WebSocket connections sending messages securely using token validation.
- Verify Redis correctly passes message states.
