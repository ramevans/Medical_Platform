The Chat models allow users to send messages to one or more users. 
Message logs are stored as documents in MongoDB collections. 
 - Each collection represents a single message log between a unique set of participants. 
 - The set of participants is what makes a message log unique and this contains all identifying information needed to store and retrieve a chat log. 
 - The set of participants MUST include the user who is sending the message and there must be more than one user.
Users can send attachments to one another. The chat model simply logs the type of media attached and a URL to its location


the API model is as followed:

 {
    "_id": "<message_id>",
    "schema_version": "<schema version>",
    "timestamp": "<timestamp the message was sent, UTC>",
    "user_id": "<user who sent the message>",
    "text": "<content of the message>",
    "attachments": [
        {
            "type": "video",
            "url": ""
        },
        {
            "type": "audio",
            "url": ""
        },
        {
            "type": "image",
            "url": ""
        },
        {
            "type": "file",
            "url": ""
        }
    ]
}
 
 I used "log_messages()" to do the logging of the files.
 
 Additional documentations can be found within the files
 
