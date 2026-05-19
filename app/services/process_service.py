from sqlalchemy.orm import Session
from app.repositories.process_repository import ProcessRepository
from app.schemas.process import ProcessCreate, ProcessUpdate
from app.models.process import Process
from app.exceptions.http_exceptions import NotFoundException, ConflictException


class ProcessService:
    def __init__(self, db: Session):
        self.repo = ProcessRepository(db)

    def create(self, data: ProcessCreate) -> Process:
        if self.repo.get_by_code(data.code):
            raise ConflictException(f"El código '{data.code}' ya existe")
        process = Process(**data.model_dump())
        return self.repo.create(process)

    def get_all(self, skip: int, limit: int) -> list[Process]:
        return self.repo.get_all(skip, limit)

    def get_by_id(self, process_id: int) -> Process:
        process = self.repo.get_by_id(process_id)
        if not process:
            raise NotFoundException("Proceso no encontrado")
        return process

    def update(self, process_id: int, data: ProcessUpdate) -> Process:
        process = self.get_by_id(process_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(process, field, value)
        return self.repo.update(process)

    def delete(self, process_id: int) -> None:
        process = self.get_by_id(process_id)
        self.repo.delete(process)