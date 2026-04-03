import streamlit_authenticator as stauth
import bcrypt # 引入底層的軍規級加密套件

def setup_authenticator():
    # 【終極解法】直接請底層 bcrypt 現場產生 '123456' 的專屬加密鎖！
    # 這樣寫完全不受 stauth 版本更新的影響，保證一定能登入
    salt = bcrypt.gensalt()
    hashed_pw = bcrypt.hashpw(b"123456", salt).decode('utf-8')

    config = {
        "credentials": {
            "usernames": {
                "commander_lin": {
                    "email": "lin@mil.edu.tw",
                    "name": "林指揮官",
                    "password": hashed_pw, # 放入現場產生的無敵加密碼
                    "role": "Commander"
                },
                "analyst_beta": {
                    "email": "analyst@mil.edu.tw",
                    "name": "戰情分析官",
                    "password": hashed_pw, # 放入現場產生的無敵加密碼
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
