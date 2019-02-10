from flask_restplus import Namespace, Resource, fields, abort
from basics import ErrorSchema, require_session, SuccessSchema
from objects import api
from flask import request
from typing import Optional, List
from models.Service import Service
from objects import db
from sqlalchemy import func
from requests import get, post
import requests.models
from vars import config
import random
import time

PublicServiceResponseSchema = api.model("Public Service Response", {
    "uuid": fields.String(example="12abc34d5efg67hi89j1klm2nop3pqrs", description="the uuid/address"),
    "name": fields.String(example="SSH", description="the name of the running service"),
    "owner": fields.String(example="12abc34d5efg67hi89j1klm2nop3pqrs", description="the owner's uuid/address"),
    "device": fields.String(example="12abc34d5efg67hi89j1klm2nop3pqrs", description="Devices uuid")
})

PrivateServiceResponseSchema = api.model("Private Service Response", {
    "uuid": fields.String(example="12abc34d5efg67hi89j1klm2nop3pqrs", description="the uuid/address"),
    "name": fields.String(example="asterix", description="the name/alias"),
    "owner": fields.String(example="12abc34d5efg67hi89j1klm2nop3pqrs", description="the owner's uuid/address"),
    "running": fields.Boolean(example=True, description="if the service is running"),
    "device": fields.String(example="12abc34d5efg67hi89j1klm2nop3pqrs", description="the device's uuid")
})

PrivateServicesResponseSchema = api.model("Private Services Resonse", {
    "services": fields.List(fields.Nested(PrivateServiceResponseSchema),
                            example="[{},{}]",
                            description="list of running services on an given device")
})

service_api = Namespace('service')

def calculate_pos(waited_time : int) -> 'int':
    """
    :param waited_time: How long the user already penetrate the service
    :return: chance that this brute force attack is successful (return , 1)
    """

    temp : int = waited_time - config["CHANCE"]

    if temp > 0:
        return 0
    else:
        return temp


@service_api.route('/public/<string:device>/<string:uuid>')
@service_api.doc("Public Service Application Programming Interface")
class PublicServiceAPI(Resource):

    @service_api.doc("Get public information about a special service running on an given device")
    @service_api.marshal_with(PublicServiceResponseSchema)
    @service_api.response(404, "Not Found", ErrorSchema)
    def get(self, device, uuid):
        device_api_response: requests.models.Response = post(config["DEVICE_API"] + "public/" + str(device)).json()

        if device_api_response.status_code == 200:
            try:
                if device_api_response["online"] != True:
                    abort(400, "Device is not online or not service found")
            except Exception:
                abort(400, "invalid device uuid")
        else:
            abort(400, "device api is offline")

        service: Optional[Service] = Service.query.filter_by(uuid=uuid, device=device).first()

        return service.serialize

    @service_api.doc("hacks a specific device")
    @service_api.response(404, "Not Found", ErrorSchema)
    @service_api.marshal_with(SuccessSchema)
    @require_session
    def post(self, session, device, uuid):
        device_api_response: request = post(config["DEVICE_API"] + "public/" + str(device)).json()

        if device_api_response.status_code == 200:
            try:
                if device_api_response["online"] != True:
                    abort(400, "invalid device uuid")
            except Exception:
                abort(400, "invalid device uuid")
        else:
            abort(400, "device api is offline")

        if "target_service" not in request.json or "target_device" not in request.json:
            abort(404, "invalid request")

        service: Optional[Service] = Service.query.filter_by(uuid=uuid, device=device).first()

        if service.target_device == request.json["target_device"] and service.target_service == request.json[
            "target_service"]:
            pen_time: int = time.time() - service.action
            if random.randint(calculate_pos(int(pen_time)),1) == 1:

                service.part_owner = session["owner"]

                return {"ok": True, "access": True, "time": pen_time}

            else:
                return {"ok": True, "access": False, "time": pen_time}

        service.use(target_service=request.json["target_service"], target_device=request.json["target_device"])

        return {"ok":True}

@service_api.route('/private/<string:device>/<string:uuid>')
@service_api.doc("Private Device Application Programming Interface")
class PrivateDeviceAPI(Resource):

    @service_api.doc("Get private information about the service")
    @service_api.marshal_with(PrivateServiceResponseSchema)
    @service_api.response(400, "Invalid Input", ErrorSchema)
    @service_api.response(403, "No Access", ErrorSchema)
    @service_api.response(404, "Not Found", ErrorSchema)
    @require_session
    def get(self, session, uuid_device, uuid_service):
        service: Optional[Service] = Service.query.filter_by(uuid=uuid_service, device=uuid_device).first()

        if service is None:
            abort(404, "invalid service uuid")

        if session["owner"] != service.owner and session["owner"] != service.part_owner:
            abort(403, "no access to this service")

        return service.serialize

    @service_api.doc("Turn the service on/off")
    @service_api.marshal_with(PrivateServiceResponseSchema)
    @service_api.response(400, "Invalid Input", ErrorSchema)
    @service_api.response(403, "No Access", ErrorSchema)
    @service_api.response(404, "Not Found", ErrorSchema)
    @require_session
    def post(self, session, uuid_device, uuid_service):
        service: Optional[Service] = Service.query.filter_by(uuid=uuid_service, device=uuid_device).first()

        if service is None:
            abort(404, "invalid service uuid")

        if session["owner"] != service.owner and session["owner"] != service.part_owner:
            abort(403, "no access to this service")

        service.running: bool = not service.running
        db.session.commit()

        return service.serialize

    @service_api.doc("Delete a service")
    @service_api.marshal_with(SuccessSchema)
    @service_api.response(400, "Invalid Input", ErrorSchema)
    @service_api.response(403, "No Access", ErrorSchema)
    @service_api.response(404, "Not Found", ErrorSchema)
    @require_session
    def delete(self, session, uuid_device, uuid_service):
        service: Optional[Service] = Service.query.filter_by(uuid=uuid_service, device=uuid_device).first()

        if service is None:
            abort(404, "invalid service uuid")

        if session["owner"] != service.owner:
            abort(403, "no access to this service")

        db.session.delete(service)
        db.session.commit()

        return {"ok": True}


@service_api.route('/private/<string:device>')
@service_api.doc("Private Device Application Programming Interface for Modifications")
class PrivateDeviceModificationAPI(Resource):

    @service_api.doc("Get all services on an given device")
    @service_api.marshal_with(PrivateServicesResponseSchema, as_list=True)
    @service_api.response(400, "Invalid Input", ErrorSchema)
    @require_session
    def get(self, session, device):
        services: List[Service] = Service.query.filter_by(owner=session["owner"], device=device).all()

        return {
            "services": [e.serialize for e in services]
        }

    @service_api.doc("Create a service on an given device")
    @service_api.marshal_with(PrivateServiceResponseSchema)
    @service_api.response(400, "Invalid Input", ErrorSchema)
    @require_session
    def put(self, session, device):
        owner: str = session["owner"]
        name: str = request.json["name"]

        available_services: List[str] = ["SSH", "Telnet", "Hydra"]

        if name not in available_services:
            abort(404, "Service is not supported")

        service_count: int = \
        (db.session.query(func.count(Service.name)).filter(Service.owner == owner, Service.device == device)).first()[0]

        if service_count != 0:
            abort(400, "you already own a service with the name " + name + " on this device")

        service: Service = Service.create(owner, device, name, True)

        return service.serialize

    @service_api.doc("Check if session owner is part owner")
    @service_api.marshal_with(SuccessSchema)
    @service_api.response(400, "Invalid Input", ErrorSchema)
    @require_session
    def post(self, session, device):
        services: List[Service] = Service.query.filter_by(device=device).all()

        for e in services:
            if e.part_owner == session["owner"]:
                return {"ok": True}

        return {"ok": False}
