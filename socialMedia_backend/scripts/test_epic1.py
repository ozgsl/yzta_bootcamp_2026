import requests
import json
import uuid

BASE_URL = "http://localhost:8000"

def run_tests():
    print("--- 1. Registering Test User ---")
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    
    reg_resp = requests.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password})
    if reg_resp.status_code != 201:
        print(f"FAILED to register: {reg_resp.text}")
        return
    user_id = reg_resp.json()["user_id"]
    print(f"SUCCESS: Registered user {user_id}")
    
    headers = {"Authorization": f"Bearer {user_id}"}
    
    print("\n--- 2. Updating Profile (PUT /users/me) ---")
    update_data = {
        "display_name": "Updated Name",
        "bio": "This is my new bio.",
        "avatar_url": "http://example.com/avatar.jpg"
    }
    prof_resp = requests.put(f"{BASE_URL}/users/me", headers=headers, json=update_data)
    if prof_resp.status_code == 200:
        print("SUCCESS: Profile updated.")
    else:
        print(f"FAILED to update profile: {prof_resp.text}")
        
    print("\n--- 3. Checking Updated Profile (GET /users/me) ---")
    get_resp = requests.get(f"{BASE_URL}/users/me", headers=headers)
    if get_resp.status_code == 200:
        data = get_resp.json()
        print(f"SUCCESS: Profile data: display_name={data.get('display_name')}, bio={data.get('bio')}")
    else:
        print(f"FAILED to get profile: {get_resp.text}")

    print("\n--- 4. Updating Privacy Settings (PUT /users/me/privacy) ---")
    priv_resp = requests.put(f"{BASE_URL}/users/me/privacy", headers=headers, json={"profile_visibility": "private"})
    if priv_resp.status_code == 200:
        print("SUCCESS: Privacy settings updated to private.")
    else:
        print(f"FAILED to update privacy: {priv_resp.text}")
        
    get_resp2 = requests.get(f"{BASE_URL}/users/me", headers=headers)
    if get_resp2.status_code == 200 and get_resp2.json().get("profile_visibility") == "private":
        print("SUCCESS: Verified profile_visibility is private.")
    else:
        print(f"FAILED: Privacy did not update properly.")

    print("\n--- 5. Reset Password (POST /auth/reset-password) ---")
    reset_resp = requests.post(f"{BASE_URL}/auth/reset-password", json={"email": email, "new_password": "new_password456"})
    if reset_resp.status_code == 200:
        print("SUCCESS: Password reset successfully.")
    else:
        print(f"FAILED to reset password: {reset_resp.text}")
        
    print("\n--- 6. Deleting Account (DELETE /users/me) ---")
    del_resp = requests.delete(f"{BASE_URL}/users/me", headers=headers)
    if del_resp.status_code == 200:
        print("SUCCESS: Account deleted.")
    else:
        print(f"FAILED to delete account: {del_resp.text}")
        
    # Verify deletion
    verify_del = requests.get(f"{BASE_URL}/users/me", headers=headers)
    if verify_del.status_code == 404:
        print("SUCCESS: Verified account is deleted (404 Not Found).")
    else:
        print(f"FAILED: Account still accessible: {verify_del.status_code}")
        
if __name__ == "__main__":
    run_tests()
