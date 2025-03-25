from dotenv import load_dotenv
import os
from pymongo import MongoClient
from datetime import datetime
from pymongo.errors import BulkWriteError
import logging

# Load MongoDB configuration from the .env file
load_dotenv()

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DATABASE = os.getenv("MONGO_DATABASE")

# Other configurations defined directly
PORTAL_NAME = "BusinessStandard"
COLLECTION_NAME = "rawnews"
BATCH_SIZE = 10  # You can adjust this as needed

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[MONGO_DATABASE]

class MongoDBPipeline:
    def __init__(self, db, collection_name, portal_name, batch_size=10):
        self.db = db
        self.collection_name = collection_name
        self.portal_name = portal_name
        self.batch_size = batch_size
        self.items = []
        self.seen_hashes = set()
        self.inserted_count = 0
        self.updated_count = 0
        self.marked_deleted_count = 0

    def process_item(self, item):
        """Process a single item (news data)."""
        hash_url = item.get('rawData', {}).get('url_hash')
        if not hash_url:
            logging.warning("Missing url_hash, skipping item.")
            return

        # Add the URL hash to the set of seen hashes
        self.seen_hashes.add(hash_url)

        # Check if the document exists in the database
        existing_doc = self.db[self.collection_name].find_one({"rawData.url_hash": hash_url, "portal": self.portal_name})

        if existing_doc:
            # Update if necessary
            if existing_doc['rawData'] != item['rawData']:
                self.db[self.collection_name].update_one(
                    {"rawData.url_hash": hash_url},
                    {
                        "$set": {
                            'isDumped': False,
                            "rawData": item['rawData'],
                            "updatedAt": datetime.utcnow().isoformat(),
                            "isUpdate": True  # Mark as updated
                        }
                    }
                )
                self.updated_count += 1
                logging.info(f"Updated news item with hash_url: {hash_url}")
            else:
                logging.info(f"No change detected for news item with hash_url: {hash_url}")
        else:
            # Insert new document if it doesn't exist
            self.db[self.collection_name].insert_one({
                'portal': self.portal_name,
                'isDumped': False,
                'rawData': item['rawData'],
                'createdAt': datetime.utcnow().isoformat(),
                'updatedAt': datetime.utcnow().isoformat(),
                'isUpdate': False,  # Mark as new insertion
                'isDeleted': False  # Not deleted
            })
            self.inserted_count += 1
            logging.info(f"Inserted new news item with hash_url: {hash_url}")

        # Add item to batch for later insertion
        self.items.append(item)

        # Batch insert when threshold is reached
        if len(self.items) >= self.batch_size:
            self.insert_batch()

    def insert_batch(self):
        """Insert the accumulated batch of items into MongoDB."""
        try:
            for item in self.items:
                raw_data = item['rawData']
                hash_url = raw_data.get('url_hash')

                # Check if the document exists
                existing_doc = self.db[self.collection_name].find_one({"rawData.url_hash": hash_url, "portal": self.portal_name})

                if existing_doc:
                    # Update if necessary (if raw_data is different)
                    if existing_doc['rawData'] != raw_data:
                        self.db[self.collection_name].update_one(
                            {"rawData.url_hash": hash_url},
                            {
                                "$set": {
                                    "rawData": raw_data,
                                    "updatedAt": datetime.utcnow().isoformat(),
                                    "isUpdate": True  # Mark as updated
                                }
                            }
                        )
                        logging.info(f"Updated existing news item with hash_url: {hash_url}")
                else:
                    # Insert new document
                    self.db[self.collection_name].insert_one({
                        'portal': self.portal_name,
                        'isDumped': False,
                        'rawData': raw_data,
                        'createdAt': datetime.utcnow().isoformat(),
                        'updatedAt': datetime.utcnow().isoformat(),
                        'isUpdate': False,  # Mark as a new insertion
                        'isDeleted': False  # Not deleted
                    })
                    logging.info(f"Inserted new news item with hash_url: {hash_url}")

            # Mark items that were not in the current batch as deleted
            self.mark_deleted_items()

            # Clear the items list after the batch insert
            self.items.clear()

        except BulkWriteError as e:
            logging.warning(f"Duplicate items found and skipped: {e.details.get('writeErrors', [])}")
        except Exception as e:
            logging.error(f"Error saving data: {e}")

    def mark_deleted_items(self):
        """Mark news items as deleted if they were not scraped in this run."""
        try:
            # Fetch all hash_urls stored in MongoDB for this portal
            stored_hashes = {doc['rawData']['url_hash'] for doc in self.db[self.collection_name].find(
                {"portal": self.portal_name}, {"rawData.url_hash": 1}
            )}

            # Identify outdated hash_urls (not found in the current batch)
            outdated_hashes = stored_hashes - self.seen_hashes

            if outdated_hashes:
                # Mark outdated items as deleted
                result = self.db[self.collection_name].update_many(
                    {"rawData.url_hash": {"$in": list(outdated_hashes)}, "portal": self.portal_name},
                    {"$set": {"isDeleted": True, "updatedAt": datetime.utcnow().isoformat()}}
                )
                self.marked_deleted_count += result.modified_count
                logging.info(f"Marked {result.modified_count} news items as deleted.")

            # Mark items in the batch as not deleted
            result = self.db[self.collection_name].update_many(
                {"rawData.url_hash": {"$in": list(self.seen_hashes)}, "portal": self.portal_name},
                {"$set": {"isDeleted": False, "isDumped": False,"updatedAt": datetime.utcnow().isoformat()}}
            )
            logging.info(f"Marked {result.modified_count} news items as active (not deleted).")

        except Exception as e:
            logging.error(f"Error marking news items as deleted: {e}")
