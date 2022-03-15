# Ramon Evans raevans@bu.edu Copyright 2022
#!/usr/bin/python3
from typing import Optional
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
import pymongo 


@dataclass
class Message:

	sender: str
	text: str
	message_id : int
	timestamp: datetime= field(default_factory=datetime.now)

	def dict_info(self):
		return asdict(self)

	@classmethod
	def input_records(cls, record: dict):
		return cls(timestamp=record['timestamp'],
				   sender=record['sender'],
					message_id=record['message_id'],
					text=record['text'])

class MessageStore:

    chat_index_collection = "chats_index"

    def __init__(self, connection_string: str, database_name: str):
        self.mongo = pymongo.MongoClient(connection_string)
        self.database = self.mongo[database_name]

    def log_message(self, user_ids: list[int], message: MessageV1):
        """Log a message to the chat log.
        Parameters
        ----------
        chat_id: str
            The identifier of the chat to send the message to.
            See `get_chat_id`
        """
        if message.sender not in user_ids:
            user_ids.append(message.sender)

        chat_id = self._get_chat_id(user_ids)
        self.database[chat_id].insert_one(message.to_dict())
        self._store_conversation_index(user_ids)

    def query_time_range(
            self,
            user_ids: list[int],
            since: Optional[datetime] = None,
            until: Optional[datetime] = None) -> list[Message]:
        """Query for chat messages within a date range.
        Parameters
        ----------
        chat_id : str
            The id of the chat to query.
        since : Optional[datetime]
            The most historcal datetime from which to consider messages. If set to None,
            it will query from the beginning of time.
        until : Optional[datetime]
            The most recent datetime to include messages from. If set to None,
            this will
        Returns
        -------
        A list of messages ordered from most historical to most recent.
        """
        query = {"timestamp": {}}
        if since is not None and until is not None:
            query["timestamp"] = {"$gt": since, "$lt": until}
        elif since is not None:
            query["timestamp"] = {"$gt": since}
        elif until is not None:
            query["timestamp"] = {"$lt": until}

        chat_id = self._get_chat_id(user_ids)
        results = self.database[chat_id].find(query).sort("timestamp")
        return [Message.from_record(record) for record in results]

    def query_latest_messages(
            self,
            user_ids: list[int],
            until: Optional[datetime] = None,
            limit=10) -> list[Message]:
        """Retrieve the last `limit` number of messages until a specified time.
        Parameters
        ----------
        user_ids : list[int]
            The users
        until : Optional[datetime]
            The date until which to consider messages. If this is none, this
            funciton will return the last `limit` messages sent in the chat.
            If set to a datetime, it will return the last `limit` messages
            before the timestamp provided.
        limit : int
            The maximum number of messages to return. Must be > 0. Default: 10
        Returns
        -------
        A list of messages ordered by timestamp from host historical to most
        recent.
        """
        query = {}
        if until is not None:
            query['timestamp'] = {"$lt": until}
        chat_id = self._get_chat_id(user_ids)
        # Sort by descending to get the latest ones
        results = (self.database[chat_id].find(query)
                                         .sort("timestamp", pymongo.DESCENDING)
                                         .limit(limit))

        # Then invert the list to put them back in time order.
        return [Message.from_record(record) for record in results][::-1]


    def _store_conversation_index(self, user_ids: set[int]):
        chat_id = self._get_chat_id(user_ids)
        collection = self.database[self.chat_index_collection]
        count = collection.count_documents({"chat_id": chat_id})
        if count == 0:
            collection.insert_one({
                "chat_id": chat_id,
                "user_ids": user_ids
            })

        if count > 1:
            LOGGER.warn(f"There are multiple records for chat id {chat_id}")

        # Create an index for chats.
        collection.create_index("user_ids", unique=True)

    def get_user_chats(self, user_ids: set[int]) -> tuple[str]:
        """Get a list of chats that a user is part of.
        Parameters
        ----------
        user_ids : set[int]
            The set (of one or more) user ids to query chat ids for. If
            multiple user ids are passed in, this function will query for
            chat that both users are part of.
        Returns
        -------
        A tuple of lists of user ids in a chat.
        """
        collection = self.database[self.chat_index_collection]
        chats = collection.find({"user_ids": {"$all": list(user_ids)}})
        return tuple([c['user_ids'] for c in chats])


def get_store_from_env():
    """Helper function to create a mongo db connection to a server
    from the following environment variables:
    MONGO_CONNECTION_STRING : str
        The connection string to the database cluser
    MONGO_CHAT_DATABASE_NAME : str
        The name of the default database to write to use
        for storing chat logs.
    Returns
    -------
    A pymongo.MongoClient instance to the specified server.
    """
    import dotenv
    import os
    dotenv.load_dotenv()
    return MessageStore(os.getenv("MONGO_CONNECTION_STRING"),
                        os.getenv("MONGO_CHAT_DATABASE_NAME"))