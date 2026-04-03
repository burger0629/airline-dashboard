import streamlit_authenticator as stauth

def setup_authenticator():
    # 建立兩個測試帳號，密碼皆為 '123456'
    # 這裡的密碼已經經過 bcrypt 雜湊加密，符合最新版 streamlit-authenticator 的安全要求
    
    config = {
        "credentials": {
            "usernames": {
                "commander_lin": {
                    "email": "lin@mil.edu.tw",
                    "name": "林指揮官",
                    "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjIQ68YlsS", # 123456 的正確雜湊值
                    "role": "Commander"
                },
                "analyst_beta": {
                    "email": "analyst@mil.edu.tw",
                    "name": "戰情分析官",
                    "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjIQ68YlsS", # 123456 的正確雜湊值
                    "role": "Analyst"
                }
            }
        },
        "cookie": {
            "expiry_days": 1,
            "key": "aviation_room_signature",
            "name": "aviation_cookie"
        },
        "pre-authorized": {
            "emails": []
        }
    }

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    
    return authenticator, config
