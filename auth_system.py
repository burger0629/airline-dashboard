import streamlit_authenticator as stauth

def setup_authenticator():
    # 【關鍵修改】讓系統即時將 '123456' 轉換成當前環境絕對支援的雜湊碼！
    passwords = ['123456', '123456']
    hashed_passwords = stauth.Hasher(passwords).generate()

    config = {
        "credentials": {
            "usernames": {
                "commander_lin": {
                    "email": "lin@mil.edu.tw",
                    "name": "林指揮官",
                    "password": hashed_passwords[0], # 使用系統自己生成的加密密碼
                    "role": "Commander"
                },
                "analyst_beta": {
                    "email": "analyst@mil.edu.tw",
                    "name": "戰情分析官",
                    "password": hashed_passwords[1], # 使用系統自己生成的加密密碼
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
