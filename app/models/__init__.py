from app.models.user import User
from app.models.role import Role
from app.models.menu import Menu
from app.models.process import Process
from app.models.person import Person                              # ← nuevo
from app.models.image import Image  
from app.models.client import Client
from app.models.chofer import Chofer  # ✅ agregar
from app.models.user_system import UserSystem  # ✅ agregar
from app.models.associations import user_roles, role_menus, menu_processes
from app.models.camion import Camion  # ✅ agregar
from app.models.taller_mecanico  import TallerMecanico
from app.models.tipo_servicio    import TipoServicio
from app.models.repuesto         import Repuesto
from app.models.servicio_mecanico import ServicioMecanico
from app.models.detalle_repuesto  import DetalleRepuesto
