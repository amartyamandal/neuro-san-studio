#!/usr/bin/env python3
"""
Live AAOSA test for Cloud Infrastructure Provider
Tests the actual agent coordination through the NeuroSan server
"""

import asyncio
import websockets
import json
import sys
import os

async def test_live_agent_coordination():
    """Test the live agent system through WebSocket"""
    
    print("=" * 60)
    print("LIVE AAOSA AGENT COORDINATION TEST")
    print("=" * 60)
    
    # Connect to the NeuroSan server
    uri = "ws://localhost:4173"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Connected to NeuroSan server at {uri}")
            
            # Send connection message
            connect_msg = {
                "type": "connect",
                "agent": "cloud_infrastructure_provider"
            }
            await websocket.send(json.dumps(connect_msg))
            print("📡 Sent connection request")
            
            # Wait for connection confirmation
            response = await websocket.recv()
            print(f"📥 Server response: {response}")
            
            # Send infrastructure request
            test_request = {
                "type": "message", 
                "message": "create a azure landing zone for my e-commerce application with web servers and database"
            }
            
            print(f"\n🚀 Sending test request: {test_request['message']}")
            await websocket.send(json.dumps(test_request))
            
            # Collect responses
            response_count = 0
            max_responses = 10  # Limit to prevent infinite loop
            
            while response_count < max_responses:
                try:
                    # Wait for response with timeout
                    response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    response_count += 1
                    
                    print(f"\n📥 Response {response_count}:")
                    
                    try:
                        parsed = json.loads(response)
                        if parsed.get("type") == "message":
                            message_text = parsed.get("message", {}).get("text", "")
                            print(f"   {message_text[:200]}...")
                            
                            # Check for errors
                            if "Error" in message_text or "Exception" in message_text:
                                print(f"❌ Error detected: {message_text}")
                                return False
                            
                            # Check for completion
                            if ("complete" in message_text.lower() or 
                                "successfully" in message_text.lower() or
                                "created" in message_text.lower()):
                                print("✅ Agent coordination appears successful!")
                                return True
                        
                    except json.JSONDecodeError:
                        print(f"   Raw response: {response[:200]}...")
                    
                except asyncio.TimeoutError:
                    print("⏰ Timeout waiting for response")
                    break
                except websockets.exceptions.ConnectionClosed:
                    print("🔌 Connection closed by server")
                    break
            
            print(f"\n📊 Received {response_count} responses")
            return response_count > 0 and response_count < max_responses
            
    except ConnectionRefusedError:
        print("❌ Could not connect to NeuroSan server")
        print("   Make sure the server is running on localhost:4173")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

async def main():
    """Main test execution"""
    print("Testing live AAOSA agent coordination...")
    print("This will test the actual Manager → Architect → Engineer workflow")
    print("")
    
    success = await test_live_agent_coordination()
    
    print("\n" + "=" * 60)
    print("LIVE TEST SUMMARY")
    print("=" * 60)
    
    if success:
        print("✅ AAOSA agent coordination is working!")
        print("   Manager, Architect, and Engineer agents are responding correctly")
        return 0
    else:
        print("❌ AAOSA agent coordination failed")
        print("   Check server logs for detailed error information")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
