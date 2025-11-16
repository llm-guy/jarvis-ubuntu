from langchain.tools import tool
import requests

HOME_ASSISTANT_URL = "http://ip:port" 
LONG_LIVED_TOKEN = ""
ENTITY_ID = "light.office_light"

@tool("toggle_office_light", return_direct=True)
def toggle_office_light(action: str) -> str:
    """
    Instantly turn the office light on or off via Home Assistant.
    action: 'on' or 'off'
    """
    action = action.lower().strip()
    if action not in ["on", "off"]:
        return "Please specify on or off, sir."

    url = f"{HOME_ASSISTANT_URL}/api/services/light/turn_{action}"
    headers = {
        "Authorization": f"Bearer {LONG_LIVED_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"entity_id": ENTITY_ID}

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=2
        )

        if response.status_code == 200:
            return f"The office light is now {action}, sir."
        else:
            return (
                f"I attempted to turn {action} the office light, "
                f"but Home Assistant returned {response.status_code}."
            )

    except requests.exceptions.ReadTimeout:
        return f"The office light should now be {action}, sir."

    except Exception:
        return (
            f"I couldn't reach Home Assistant just now, sir. "
            f"The office light may not have changed."
        )
