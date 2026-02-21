# netlify/functions/api.py
import json
import time
import random
import hashlib
import requests

MI_API_URL_STATUS = "https://sgp-api.buy.mi.com/bbs/api/global/user/bl-switch/state"
MI_API_URL_APPLY = "https://sgp-api.buy.mi.com/bbs/api/global/apply/bl-auth"

def generate_device_id(token):
    random_data = f"{random.random()}-{time.time()}-{token}"
    return hashlib.sha1(random_data.encode('utf-8')).hexdigest().upper()

def get_headers(token, device_id):
    return {
        "Cookie": f"new_bbs_serviceToken={token};versionCode=500411;versionName=5.4.11;deviceId={device_id};",
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "okhttp/4.12.0"
    }

def handler(event, context):
    if event['httpMethod'] != 'POST':
        return {
            'statusCode': 405,
            'body': json.dumps({'status': 'error', 'message': 'Method Not Allowed'})
        }

    try:
        body = json.loads(event['body'])
        token = body.get('token', '').strip()
    except:
        return {
            'statusCode': 400,
            'body': json.dumps({'status': 'error', 'message': 'Bad Request: Invalid JSON'})
        }

    if not token:
        return {
            'statusCode': 400,
            'body': json.dumps({'status': 'error', 'message': 'Token is required'})
        }

    device_id = generate_device_id(token)
    headers = get_headers(token, device_id)
    logs = [f"Generated Device ID: {device_id}"]

    # 1. Check Status
    try:
        logs.append("Checking current status...")
        resp = requests.get(MI_API_URL_STATUS, headers=headers, timeout=10)
        resp_json = resp.json()
        code = resp_json.get("code")
        data_obj = resp_json.get("data", {})
        
        if code == 100004:
            return {'statusCode': 200, 'body': json.dumps({"status": "error", "logs": logs, "message": "Cookie/Token is expired."})}
        
        is_pass = data_obj.get("is_pass")
        button_state = data_obj.get("button_state")
        deadline = data_obj.get("deadline_format", "Unknown")

        if is_pass == 1:
            logs.append(f"Status: Approved! Unlock possible until {deadline}")
            return {'statusCode': 200, 'body': json.dumps({"status": "success", "logs": logs, "message": "Already Approved"})}
        
        if is_pass == 4 and button_state == 2:
             logs.append(f"Status: Blocked until {deadline}")
             return {'statusCode': 200, 'body': json.dumps({"status": "error", "logs": logs, "message": f"Account blocked until {deadline}"})}

    except Exception as e:
        logs.append(f"Error checking status: {str(e)}")
        return {'statusCode': 500, 'body': json.dumps({"status": "error", "logs": logs, "message": "Network error checking status"})}

    # 2. Apply for Unlock
    try:
        logs.append("Sending unlock request...")
        post_body = {"is_retry": True} 
        resp = requests.post(MI_API_URL_APPLY, headers=headers, json=post_body, timeout=10)
        resp_json = resp.json()
        code = resp_json.get("code")
        msg = resp_json.get("message", "")
        data_obj = resp_json.get("data", {})
        logs.append(f"Response Code: {code} | Message: {msg}")

        response_body = {}
        if code == 0:
            apply_result = data_obj.get("apply_result")
            if apply_result == 1:
                response_body = {"status": "success", "logs": logs, "message": "Application Approved!"}
            elif apply_result == 3:
                deadline = data_obj.get("deadline_format", "")
                response_body = {"status": "warning", "logs": logs, "message": f"Limit exceeded. Try again: {deadline}"}
            else:
                response_body = {"status": "success", "logs": logs, "message": f"Request sent. Result: {apply_result}"}
        else:
             response_body = {"status": "error", "logs": logs, "message": f"API Error: {msg}"}
        
        return {'statusCode': 200, 'body': json.dumps(response_body)}

    except Exception as e:
        logs.append(f"Error sending request: {str(e)}")
        return {'statusCode': 500, 'body': json.dumps({"status": "error", "logs": logs, "message": "Network error sending request"})}
