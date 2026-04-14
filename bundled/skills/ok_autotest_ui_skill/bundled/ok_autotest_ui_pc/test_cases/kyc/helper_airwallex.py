"""
Airwallex Helper Module
Helper functions for interacting with Redis, PostgreSQL, and Airwallex API
"""
import redis
import psycopg2
import requests
import json
from typing import Optional, Dict, Any
from datetime import datetime

# Try to import loguru, fall back to simple logger if not available
try:
    from loguru import logger
except ImportError:
    class SimpleLogger:
        @staticmethod
        def log(level, message):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] [{level}] {message}")
        
        @staticmethod
        def info(message):
            SimpleLogger.log("INFO", message)
        
        @staticmethod
        def success(message):
            SimpleLogger.log("SUCCESS", message)
        
        @staticmethod
        def warning(message):
            SimpleLogger.log("WARNING", message)
        
        @staticmethod
        def error(message):
            SimpleLogger.log("ERROR", message)
        
        @staticmethod
        def debug(message):
            SimpleLogger.log("DEBUG", message)
    
    logger = SimpleLogger()


class AirwallexHelper:
    """Helper class for Airwallex account status management"""
    
    # Redis Configuration
    REDIS_HOST = "redis-shark-test.rdb.58dns.org"
    REDIS_PORT = 50554
    REDIS_PASSWORD = "6b0d1d0d640eb6fa"
    REDIS_TOKEN_KEY = b"\xac\xed\x00\x05t\x00\x0fairwallex:token"
    
    # PostgreSQL Configuration
    DB_HOST = "pgsql-test.pdb.58dns.org"
    DB_PORT = 29000
    DB_NAME = "pdb58_easypost"
    DB_USER = "epost_test"
    DB_PASSWORD = "GUGXzw49K6Ndp7"
    
    # Airwallex API Configuration
    API_BASE_URL = "https://api-demo.airwallex.com/api/v1"
    
    def __init__(self):
        """Initialize helper"""
        self.redis_client: Optional[redis.Redis] = None
        self.db_connection: Optional[psycopg2.extensions.connection] = None
        
    def connect_redis(self) -> redis.Redis:
        """
        Connect to Redis server
        
        Returns:
            redis.Redis: Redis client instance
        """
        try:
            self.redis_client = redis.Redis(
                host=self.REDIS_HOST,
                port=self.REDIS_PORT,
                password=self.REDIS_PASSWORD,
                decode_responses=False  # Keep binary data as-is
            )
            # Test connection
            self.redis_client.ping()
            logger.info(f"Successfully connected to Redis: {self.REDIS_HOST}:{self.REDIS_PORT}")
            return self.redis_client
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def get_token_from_redis(self) -> str:
        """
        Get Airwallex token from Redis
        
        Returns:
            str: Airwallex Bearer token
        """
        try:
            if not self.redis_client:
                self.connect_redis()
            
            # Get token from Redis (binary data)
            token_bytes = self.redis_client.get(self.REDIS_TOKEN_KEY)
            
            if not token_bytes:
                raise ValueError("Token not found in Redis")
            
            # The token is stored as serialized Java object, need to extract the actual token
            # Try to decode and find the JWT token pattern
            try:
                token = token_bytes.decode('latin-1')
                # Look for JWT token with timestamp pattern first
                import re
                expiry_pattern = r'(eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+):(\d+)'
                expiry_match = re.search(expiry_pattern, token)
                if expiry_match:
                    # Use only the JWT part, WITHOUT the timestamp
                    token = expiry_match.group(1)
                    logger.info(f"Extracted JWT token (without timestamp)")
                else:
                    # Fallback: look for JWT token pattern without timestamp
                    jwt_pattern = r'(eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+)'
                    jwt_match = re.search(jwt_pattern, token)
                    if jwt_match:
                        token = jwt_match.group(1)
                    else:
                        # If no JWT found, use the whole content
                        pass
            except Exception as e:
                logger.warning(f"Token extraction warning: {e}")
                token = token_bytes.decode('latin-1')
            
            logger.info(f"Successfully retrieved token from Redis (length: {len(token)})")
            return token
        except Exception as e:
            logger.error(f"Failed to get token from Redis: {e}")
            raise
    
    def connect_database(self) -> psycopg2.extensions.connection:
        """
        Connect to PostgreSQL database
        
        Returns:
            psycopg2.extensions.connection: Database connection
        """
        try:
            self.db_connection = psycopg2.connect(
                host=self.DB_HOST,
                port=self.DB_PORT,
                database=self.DB_NAME,
                user=self.DB_USER,
                password=self.DB_PASSWORD
            )
            logger.info(f"Successfully connected to database: {self.DB_NAME}")
            return self.db_connection
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def get_payment_account_id(self, app_user_id: str) -> Optional[str]:
        """
        Get payment account ID from database for a specific user
        
        Args:
            app_user_id: Application user ID
            
        Returns:
            str: Payment account ID or None if not found
        """
        try:
            if not self.db_connection:
                self.connect_database()
            
            cursor = self.db_connection.cursor()
            query = """
                SELECT payment_account_id 
                FROM user_payment_binding 
                WHERE app_user_id = %s 
                ORDER BY id DESC 
                LIMIT 1
            """
            
            cursor.execute(query, (app_user_id,))
            result = cursor.fetchone()
            cursor.close()
            
            if result and result[0]:
                payment_account_id = result[0]
                logger.info(f"Found payment_account_id: {payment_account_id} for user: {app_user_id}")
                return payment_account_id
            else:
                logger.warning(f"No payment account found for user: {app_user_id}")
                return None
        except Exception as e:
            logger.error(f"Failed to get payment account ID: {e}")
            raise
    
    def update_account_status(
        self, 
        payment_account_id: str, 
        token: str, 
        status: str = "ACTIVE",
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Update Airwallex account status via API
        
        Args:
            payment_account_id: Payment account ID
            token: Bearer token for authentication
            status: Target status - "ACTIVE" or "SUSPENDED"
            force: Force update flag
            
        Returns:
            dict: API response
        """
        try:
            url = f"{self.API_BASE_URL}/simulation/accounts/{payment_account_id}/update_status"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
            
            payload = {
                "force": force,
                "next_status": status
            }
            
            logger.info(f"Sending request to update account status to {status}")
            logger.debug(f"URL: {url}")
            logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            logger.info(f"Response status code: {response.status_code}")
            
            try:
                response_data = response.json()
                logger.debug(f"Response body: {json.dumps(response_data, indent=2)}")
            except ValueError:
                response_data = {"raw_text": response.text}
                logger.debug(f"Response text: {response.text}")
            
            if response.status_code in [200, 201]:
                logger.success(f"Successfully updated account status to {status}")
            else:
                logger.warning(f"Request completed with status code: {response.status_code}")
            
            return {
                "status_code": response.status_code,
                "success": response.status_code in [200, 201],
                "response": response_data,
                "request_url": url,
                "request_payload": payload
            }
        except Exception as e:
            logger.error(f"Failed to update account status: {e}")
            raise
    
    def activate_account(self, payment_account_id: str, token: str, force: bool = False) -> Dict[str, Any]:
        """
        Activate (verify success) Airwallex account
        
        Args:
            payment_account_id: Payment account ID
            token: Bearer token
            force: Force update flag
            
        Returns:
            dict: API response
        """
        logger.info(f"Activating account: {payment_account_id}")
        return self.update_account_status(payment_account_id, token, status="ACTIVE", force=force)
    
    def suspend_account(self, payment_account_id: str, token: str, force: bool = False) -> Dict[str, Any]:
        """
        Suspend (verify failure) Airwallex account
        
        Args:
            payment_account_id: Payment account ID
            token: Bearer token
            force: Force update flag
            
        Returns:
            dict: API response
        """
        logger.info(f"Suspending account: {payment_account_id}")
        return self.update_account_status(payment_account_id, token, status="SUSPENDED", force=force)
    
    def close(self):
        """Close all connections"""
        if self.redis_client:
            try:
                self.redis_client.close()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.warning(f"Error closing Redis connection: {e}")
        
        if self.db_connection:
            try:
                self.db_connection.close()
                logger.info("Database connection closed")
            except Exception as e:
                logger.warning(f"Error closing database connection: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
