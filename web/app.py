import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin.contrib.sqla import Admin, ModelView
from web.provider import UsernameAndPasswordProvider
from bot.db.models import engine, User, Product, Category, Lesson

app = Starlette()
admin = Admin(
    engine=engine,
    title="Admin Panel",
    base_url='/',
    auth_provider=UsernameAndPasswordProvider(),
    middlewares=[Middleware(SessionMiddleware, secret_key="qewrerthytju4")]
)

class AllModelView(ModelView):
    exclude_fields_from_create = ["created_at", "updated_at", "products"]

admin.add_view(AllModelView(User))
admin.add_view(AllModelView(Product))
admin.add_view(AllModelView(Category))
admin.mount_to(app)
admin.add_view(AllModelView(Lesson))

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)