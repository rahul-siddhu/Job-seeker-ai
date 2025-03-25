import pymongo
from datetime import datetime
from scrapy.exceptions import DropItem
from pymongo.errors import BulkWriteError

class MongoPipeline:
    collection_name = 'rawjobs'

    def __init__(self, mongo_uri, mongo_db, batch_size=200, portal_name='Timesjobs'):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.batch_size = batch_size
        self.portal_name = portal_name  # Portal-specific deletion
        self.items = []  # Batch list for new insertions
        self.inserted_count = 0  # Track the number of inserted jobs
        self.updated_count = 0  # Track the number of updated jobs
        self.marked_deleted_count = 0  # Track the number of jobs marked as deleted
        self.seen_job_ids = set()  # Track job IDs seen during this scrape

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items'),
            batch_size=crawler.settings.get('BATCH_SIZE', 200),
            portal_name=crawler.settings.get('PORTAL_NAME', 'Timesjobs')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        spider.logger.info(f"MongoDB pipeline initialized for database: {self.mongo_db}, portal: {self.portal_name}")

    def close_spider(self, spider):
        if self.items:
            self.insert_batch(spider)

        # Mark outdated jobs as deleted
        self.mark_deleted_jobs(spider)

        # Log summary of inserted, updated, and marked-deleted jobs
        spider.logger.info(f"Total inserted jobs: {self.inserted_count}")
        spider.logger.info(f"Total updated jobs: {self.updated_count}")
        spider.logger.info(f"Total jobs marked as deleted: {self.marked_deleted_count}")

        self.client.close()

    def process_item(self, item, spider):
        job_id = item['rawData'].get('id')  
        if not job_id:
            spider.logger.warning("No job ID found, skipping item.")
            return item

        self.seen_job_ids.add(job_id)

        # Check if the job already exists in MongoDB
        existing_job = self.db[self.collection_name].find_one({"rawData.id": job_id, "portal": self.portal_name})

        if existing_job:
            # Update the existing job if the data has changed
            if existing_job['rawData'] != item['rawData']:
                self.db[self.collection_name].update_one(
                    {"rawData.id": job_id, "portal": self.portal_name},
                    {"$set": {
                        "rawData": item['rawData'],
                        "updatedAt": datetime.utcnow().isoformat(),
                        "isDeleted": False,  # Mark as not deleted
                        "isUpdate": True  # Mark as updated
                    }}
                )
                self.updated_count += 1
                spider.logger.info(f"Updated existing job with ID: {job_id}")
            else:
                raise DropItem(f"No changes detected for job ID: {job_id}")
        else:
            # Insert new job data
            self.items.append({
                'portal': self.portal_name,  
                'isDumped': False,  # Additional field if required
                'rawData': item['rawData'],
                'isDeleted': False,  # New jobs are not marked as deleted
                'isUpdate': False,  # New jobs are not updates
                'createdAt': datetime.utcnow().isoformat(),
                'updatedAt': datetime.utcnow().isoformat(),
            })
            self.inserted_count += 1
            spider.logger.info(f"Inserted new job with ID: {job_id}")

        if len(self.items) >= self.batch_size:
            self.insert_batch(spider)

        return item

    def insert_batch(self, spider):
        """Insert the accumulated batch of items into MongoDB."""
        try:
            self.db[self.collection_name].insert_many(self.items, ordered=False)
            spider.logger.info(f"Inserted {len(self.items)} items to MongoDB in batch.")
        except BulkWriteError as e:
            spider.logger.warning(f"Duplicate items found and skipped: {e.details.get('writeErrors', [])}")
        finally:
            self.items.clear()

    def mark_deleted_jobs(self, spider):
        """Mark jobs as deleted if they were not scraped in this run."""
        try:
            # Get job IDs currently stored in MongoDB for this portal
            stored_job_ids = {doc['rawData']['id'] for doc in self.db[self.collection_name].find(
                {"portal": self.portal_name}, {"rawData.id": 1}
            )}

            # Find job IDs that were not scraped in the current session
            outdated_job_ids = stored_job_ids - self.seen_job_ids

            if outdated_job_ids:
                # Mark outdated jobs as deleted for this portal
                result = self.db[self.collection_name].update_many(
                    {"rawData.id": {"$in": list(outdated_job_ids)}, "portal": self.portal_name},
                    {"$set": {"isDeleted": True, "isUpdate": False, "updatedAt": datetime.utcnow().isoformat()}}
                )
                self.marked_deleted_count += result.modified_count
                spider.logger.info(f"Marked {result.modified_count} jobs as deleted for portal: {self.portal_name}")
        except Exception as e:
            spider.logger.error(f"Error during marking deleted jobs: {e}")
