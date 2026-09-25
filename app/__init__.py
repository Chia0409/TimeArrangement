# from flask import Flask
# from config import Config

# first
# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(Config)

#     # 暫時測試用路由，之後這裡會換成正式的首頁/預計任務/任務總結三個blueprint
#     @app.route("/")
#     def hello():
#         return f"Flask 環境設定成功！目前連線的資料庫設定是：{app.config['DB_NAME']}"

#     return app

# source /Users/changting-chia/4.TimeArrangement/venv/bin/activate
# (base) changting-chia@zhangtingjiadeMacBook-Air 4.TimeArrangement % source /Users/changting-chia/4.TimeArrangement/venv/bin/activate
# (venv) (base) changting-chia@zhangtingjiadeMacBook-Air 4.TimeArrangement % deactivate
# (base) changting-chia@zhangtingjiadeMacBook-Air 4.TimeArrangement % source venv/bin/activate
# (venv) (base) changting-chia@zhangtingjiadeMacBook-Air 4.TimeArrangement % 


# second
# from flask import Flask
# from config import Config
# from app.db import init_app as init_db
# from app.repositories.mission_repo import get_missions_by_date


# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(Config)
#     init_db(app)   # 新增：註冊資料庫連線的收尾機制

#     @app.route("/")
#     def hello():
#         missions = get_missions_by_date("2026-09-17")
#         return f"資料庫連線成功！2026-09-17 共有 {len(missions)} 筆任務資料。"

#     return app

# third + fourth plan_bp
from flask import Flask, session
from config import Config
from app.db import init_app as init_db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    init_db(app)

    from app.routes.home import home_bp   # 延遲匯入，避免跟app/__init__.py互相import造成循環匯入
    from app.routes.plan import plan_bp   # forth
    from app.routes.summary import summary_bp  # fifth
    from app.routes.auth import auth_bp # user_add

    app.register_blueprint(home_bp)
    app.register_blueprint(plan_bp) # forth
    app.register_blueprint(summary_bp) # fifth
    app.register_blueprint(auth_bp) # user_add

    @app.context_processor
    def inject_current_user():
        from app.repositories.user_repo import get_user_by_id
        user = get_user_by_id(session["user_id"]) if "user_id" in session else None
        return {"current_user": user}


    return app



