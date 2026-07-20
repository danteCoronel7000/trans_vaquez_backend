import cloudinary
import cloudinary.uploader
from app.core.config import settings

# Configuración global — se ejecuta una vez al importar
cloudinary.config(
    cloud_name = settings.CLOUDINARY_CLOUD_NAME,
    api_key    = settings.CLOUDINARY_API_KEY,
    api_secret = settings.CLOUDINARY_API_SECRET,
    secure     = True   # URLs con HTTPS
)


class CloudinaryService:

    def upload(self, file_bytes: bytes, filename: str) -> dict:
        """
        Sube un archivo a Cloudinary.
        Retorna un dict con url y public_id entre otros datos.
        En Spring Boot usabas MultipartFile.getBytes(),
        acá recibís los bytes directamente desde FastAPI.
        """
        result = cloudinary.uploader.upload(
            file_bytes,
            folder        = "transport/persons",  # carpeta en Cloudinary
            resource_type = "image",
            use_filename  = True,
            unique_filename = True,
        )
        return result

    def delete(self, public_id: str) -> dict:
        """
        Elimina una imagen de Cloudinary por su public_id.
        Equivalente al destroy() de Spring Boot.
        """
        result = cloudinary.uploader.destroy(
            public_id,
            resource_type = "image"
        )
        return result


# Instancia singleton — igual que @Service de Spring Boot
cloudinary_service = CloudinaryService()