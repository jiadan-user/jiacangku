#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to connect to Redis and get the airwallex:token value
"""
import sys
import redis

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Redis connection parameters
REDIS_HOST = "redis-shark-test.rdb.58dns.org"
REDIS_PORT = 50554
REDIS_PASSWORD = "6b0d1d0d640eb6fa"

# The key to retrieve (with byte escape sequences)
KEY = b"\xac\xed\x00\x05t\x00\x0fairwallex:token"

def main():
    try:
        # Connect to Redis
        print(f"Connecting to Redis at {REDIS_HOST}:{REDIS_PORT}...")
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=False  # Keep as bytes to handle binary keys
        )
        
        # Test connection
        r.ping()
        print("[OK] Connected successfully!")
        
        # Get the value
        print(f"\nExecuting: GET {KEY!r}")
        value = r.get(KEY)
        
        if value is None:
            print("Key not found or value is None")
        else:
            print(f"\nValue (raw bytes length): {len(value)} bytes")
            print(f"\nFirst few bytes (hex): {value[:20].hex()}")
            
            # The value appears to be Java serialized with a prefix
            # Skip the Java serialization header and extract the actual token
            # Pattern: \xac\xed\x00\x05t\x02^ indicates Java serialized string
            # Let's try to extract the JWT token part
            try:
                # Find where the actual token starts (after the Java serialization prefix)
                token_start = value.find(b'eyJ')  # JWT tokens typically start with eyJ
                if token_start != -1:
                    # The token format appears to be: TOKEN:TIMESTAMP
                    token_data = value[token_start:].decode('utf-8')
                    print(f"\n{'='*80}")
                    print("EXTRACTED TOKEN DATA:")
                    print(f"{'='*80}")
                    print(token_data)
                    print(f"{'='*80}")
                    
                    # Split token and timestamp if colon exists
                    if ':' in token_data:
                        token, timestamp = token_data.rsplit(':', 1)
                        print(f"\nJWT Token:\n{token}")
                        print(f"\nTimestamp: {timestamp}")
                    else:
                        print(f"\nJWT Token:\n{token_data}")
                else:
                    print("\n[WARNING] Could not find JWT token pattern in the value")
                    print(f"Raw value:\n{value!r}")
            except Exception as decode_err:
                print(f"\n[ERROR] Failed to decode token: {decode_err}")
                print(f"Hex dump:\n{value.hex()}")
        
    except redis.ConnectionError as e:
        print(f"[ERROR] Connection error: {e}")
    except redis.AuthenticationError as e:
        print(f"[ERROR] Authentication error: {e}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
