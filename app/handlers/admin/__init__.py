from .admin_panel import router as panel_router
from .admin_stats import router as stats_router  
from .admin_user_mgmt import router as users_router
from .admin_games_mgmt import router as games_router
from .admin_mgmt import router as admins_router

# Все админские роутеры для импорта в главный файл
admin_routers = [
    panel_router,
    stats_router,
    users_router, 
    games_router,
    admins_router
]