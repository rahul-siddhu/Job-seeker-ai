import logging
from scraper import scrape_news
from data_dump import MongoDBPipeline
from dotenv import load_dotenv
import os

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def main():
    """
    Main function to initialize and coordinate scraping and data insertion.
    """
    try:
        logging.info("Starting the news scraping process...")

        # Load configuration from environment variables
        db_uri = os.getenv("MONGO_URI")
        db_name = os.getenv("MONGO_DATABASE")
        
        if not db_uri or not db_name:
            logging.error("Error: Missing required environment variables 'MONGO_URI' or 'MONGO_DATABASE'.")
            return
        
        # Additional configuration
        collection_name = os.getenv("MONGO_COLLECTION", "rawnews")
        portal_name = os.getenv("PORTAL_NAME", "BusinessStandard")

        # Initialize MongoDB pipeline
        logging.info("Initializing MongoDB pipeline...")
        pipeline = MongoDBPipeline(db_uri, db_name, collection_name, portal_name)

        # Start the scraping process
        logging.info("Starting the scraper...")
        scrape_news(pipeline)  # Pass pipeline to scraper

        logging.info("Scraping and data insertion completed successfully.")
    
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
    
    finally:
        logging.info("Process completed.")

if __name__ == "__main__":
    main()
