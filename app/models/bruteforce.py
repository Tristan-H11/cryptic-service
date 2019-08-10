from typing import Union

from sqlalchemy import Column, BigInteger, String

from app import wrapper


class Bruteforce(wrapper.Base):
    __tablename__: str = "bruteforce"

    uuid: Union[Column, str] = Column(String(36), primary_key=True, unique=True)
    started: Union[Column, int] = Column(BigInteger)
    target_service: Union[Column, str] = Column(String(36))
    target_device: Union[Column, str] = Column(String(36))

    @property
    def serialize(self):
        _: str = self.uuid
        d: dict = self.__dict__.copy()

        del d['_sa_instance_state']

        return d

    @staticmethod
    def create(uuid: str) -> 'Bruteforce':
        """
        Creates a new service.
        :param uuid: uuid of the service
        :return: New DeviceModel
        """

        service = Bruteforce(
            uuid=uuid,
            started=None,
            target_service=None,
            target_device=None
        )

        wrapper.session.add(service)
        wrapper.session.commit()

        return service