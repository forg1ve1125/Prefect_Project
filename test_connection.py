import asyncio
from prefect import get_client
import sys

# Disable logging configuration if possible before import? 
# No, prefect imports it at top level.

async def test():
    print("Testing client connection...")
    try:
        async with get_client() as client:
            print("Client connected!")
            # Try a simple call
            try:
                me = await client.hello()
                print("Hello success")
            except:
                print("Skipping hello check")
                
    except Exception as e:
        print(f"Client failure: {e}")

if __name__ == "__main__":
    asyncio.run(test())
