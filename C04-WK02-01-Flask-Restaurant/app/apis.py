from app import application
from flask import jsonify, Response, session
from app.models import *
from app import *
import uuid
import datetime
from marshmallow import Schema, fields
from flask_restful import Resource, Api
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
import json

class SignUpRequest(Schema):
    name = fields.Str()
    username = fields.Str()
    password = fields.Str()
    level = fields.Int()

class LoginRequest(Schema):
    username = fields.Str(default="username")
    password = fields.Str(default="password")

class APIResponse(Schema):
    message = fields.Str(default="Success")

class AddVendorRequest(Schema):
    user_id = fields.Str(default="1234")

class VendorsListResponse(Schema):
    vendors = fields.List(fields.Dict())

class AddItemRequest(Schema):
    item_name  = fields.Str(default="item name")
    calories_per_gm = fields.Int(default=100)
    available_quantity = fields.Int(default=100)
    restaurant_name = fields.Str(default="hotel name")
    unit_price = fields.Int(default=0)

class ItemListResponse(Schema):
    items = fields.List(fields.Dict())

class ItemsOrderList(Schema):
    items = fields.List(fields.Dict())

class PlaceOrderRequest(Schema):
    order_id = fields.Str(default="order_id")

class ListOrderResponse(Schema):
    orders = fields.List(fields.Dict())

#  Restful way of creating APIs through Flask Restful
class SignUpAPI(MethodResource, Resource):
    @doc(description='Sign Up API', tags=['SignUp API'])
    @use_kwargs(SignUpRequest, location=('json'))
    @marshal_with(APIResponse)  # marshalling
    def post(self, **kwargs):
        try:
            user = User(
                uuid.uuid4(),
                kwargs['name'], 
                kwargs['username'], 
                kwargs['password'], 
                kwargs['level'])
            db.session.add(user)
            db.session.commit()
            return APIResponse().dump(dict(message='User is successfully registered')), 200
            # return jsonify({'message':'User is successfully registerd'}), 200
        
        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to register user : {str(e)}')), 400
            # return jsonify({'message':f'Not able to register user : {str(e)}'}), 400

api.add_resource(SignUpAPI, '/signup')
docs.register(SignUpAPI)

class LoginAPI(MethodResource, Resource):
    @doc(description='Login API', tags=['Login API'])
    @use_kwargs(LoginRequest, location=('json'))
    @marshal_with(APIResponse)  # marshalling
    def post(self, **kwargs):
        try:
            user = User.query.filter_by(username=kwargs['username'], password = kwargs['password']).first()
            if user:
                print('logged in')
                session['user_id'] = user.user_id
                session_userid = session['user_id']
                # if session_userid == 0:
                #     print('customer')
                # elif session_userid == 1:
                #     print('vendor')
                # elif session_userid == 2:
                #     print('admin')         
                print(f'User id : {str(session["user_id"])}')
                
                return APIResponse().dump(dict(message='User is successfully logged in')), 200
                # return jsonify({'message':'User is successfully logged in'}), 200
            else:
                return APIResponse().dump(dict(message='User not found')), 404
                # return jsonify({'message':'User not found'}), 404
        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to login user : {str(e)}')), 400
            # return jsonify({'message':f'Not able to login user : {str(e)}'}), 400

api.add_resource(LoginAPI, '/login')
docs.register(LoginAPI)

class LogoutAPI(MethodResource, Resource):
    @doc(description='Logout API', tags=['Logout API'])
    @marshal_with(APIResponse)  # marshalling
    def post(self, **kwargs):
        try:
            if session['user_id']:
                session['user_id'] = None
                print('logged out')
                return APIResponse().dump(dict(message='User is successfully logged out')), 200
                # return jsonify({'message':'User is successfully logged out'}), 200
            else:
                print('user not found')
                return APIResponse().dump(dict(message='User is not logged in')), 401
                # return jsonify({'message':'User is not logged in'}), 401
        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to logout user : {str(e)}')), 400
            # return jsonify({'message':f'Not able to logout user : {str(e)}'}), 400

    pass
            

api.add_resource(LogoutAPI, '/logout')
docs.register(LogoutAPI)


class AddVendorAPI(MethodResource, Resource):
    @doc(description='Add Vendor API', tags=['AddVendor API'])
    @use_kwargs(AddVendorRequest, location=('json'))
    @marshal_with(APIResponse)  # marshalling
    def post(self, **kwargs):
        try:
            if session['user_id']:
                user_id = session['user_id']
                user_type = User.query.filter_by(user_id=user_id).first().level
                if user_type  == 2:
                    vendor_user_id = kwargs['user_id']
                    user = User.query.filter_by(user_id=vendor_user_id).first()
                    user.level = 1
                    db.session.commit()
                    return APIResponse().dump(dict(message='Vendor is successfully added.')), 200

            return APIResponse().dump(dict(message='User is successfully added as Vendor')), 200
            # return jsonify({'message':'User is successfully registerd'}), 200
        
        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to add user as Vendor : {str(e)}')), 400
            # return jsonify({'message':f'Not able to register user : {str(e)}'}), 400

    pass


api.add_resource(AddVendorAPI, '/add_vendor')
docs.register(AddVendorAPI)


class GetVendorsAPI(MethodResource, Resource):
    @doc(description='Get All Vendors API', tags=['Get Vendor API'])
    @marshal_with(VendorsListResponse)  # marshalling
    def get(self):
        try:
            if session['user_id']:
                user_id = session['user_id']
                user_type = User.query.filter_by(user_id=user_id).first().level
                print(user_id)
                if user_type  == 2:
                    vendors = User.query.filter_by(level=1)
                    vendors_list = list()
                    for vendor in vendors:
                        vendor_dict = dict()
                        vendor_dict['vendor_id'] = vendor.user_id
                        vendor_dict['name'] = vendor.name
                        vendors_list.append(vendor_dict)
            return VendorsListResponse().dump(dict(vendors = vendors_list)), 200

        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to list vendors : {str(e)}')), 400

    pass
            

api.add_resource(GetVendorsAPI, '/list_vendors')
docs.register(GetVendorsAPI)

class AddItemAPI(MethodResource, Resource):

    @doc(description='Add Item API', tags=['Add Items API'])
    @use_kwargs(AddItemRequest, location=('json'))
    @marshal_with(APIResponse)  # marshalling
    def post(self, **kwargs):
        try:
            if session['user_id']:
                user_id = session['user_id']
                user_type = User.query.filter_by(user_id=user_id).first().level
                if user_type  == 1:
                    item = Item(
                        uuid.uuid4(),
                        session['user_id'],
                        kwargs['item_name'],
                        kwargs['calories_per_gm'],
                        kwargs['available_quantity'],
                        kwargs['restaurant_name'],
                        kwargs['unit_price']
                    )
                    db.session.add(item)
                db.session.commit()
            return APIResponse().dump(dict(message='Item is successfully added.')), 200

        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to list vendors : {str(e)}')), 400

    pass
            

api.add_resource(AddItemAPI, '/add_item')
docs.register(AddItemAPI)


class ListItemsAPI(MethodResource, Resource):
    @doc(description='List All Items API', tags=['List Items API'])
    # @marshal_with(ItemListResponse)  # marshalling
    def get(self):
        try:
            if session['user_id']:
                    items = Item.query.all()
                    items_list = list()
                    for item in items:
                        item_dict = dict()
                        item_dict['item_id'] = item.item_id
                        item_dict['item_name'] = item.item_name
                        item_dict['calories_per_gm'] = item.calories_per_gm
                        item_dict['available_quantity'] = item.available_quantity
                        item_dict['unit_price'] = item.unit_price

                        items_list.append(item_dict)
                        
            return ItemListResponse().dump(dict(items = items_list)), 200
        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to list items : {str(e)}')), 400
    pass

api.add_resource(ListItemsAPI, '/list_items')
docs.register(ListItemsAPI)


class CreateItemOrderAPI(MethodResource, Resource):
    @doc(description='Create Items Order API', tags=['Create Order API'])
    @use_kwargs(ItemsOrderList, location=('json'))
    @marshal_with(APIResponse)  # marshalling
    def post(self, **kwargs):
        try:
            if session['user_id']:
                user_id = session['user_id']
                user_type = User.query.filter_by(user_id=user_id).first().level
                if user_type  == 0:
                    order_id = uuid.uuid4()
                    order = Order(order_id, user_id)
                    db.session.add(order)
                    
                    for item in kwargs['items']:
                        item = dict(item)
                        order_item = OrderItems(
                            uuid.uuid4(),
                            order_id,
                            item['item_id'],
                            item['quantity']
                        )
                        db.session.add(order_item)
                    
                    db.session.commit()
            return APIResponse().dump(dict(message=f'Items for the Order are successfully added with order id : {order_id}')), 200

        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to add items for ordering : {str(e)}')), 400

    pass
            

api.add_resource(CreateItemOrderAPI, '/create_items_order')
docs.register(CreateItemOrderAPI)


class PlaceOrderAPI(MethodResource, Resource):
    @doc(description='Place Order API', tags=['Place Order API'])
    @use_kwargs(PlaceOrderRequest, location=('json'))
    @marshal_with(APIResponse)  # marshalling
    def post(self, **kwargs):
        try:
            if session['user_id']:
                user_id = session['user_id']
                user_type = User.query.filter_by(user_id=user_id).first().level

                if user_type  == 0:
                    order_items = OrderItems.query.filter_by(order_id=kwargs['order_id'], is_active=1)
                    order = Order.query.filter_by(order_id=kwargs['order_id'], is_active=1).first()
                    total_amount = 0

                    for order_item in order_items:
                        item_id = order_item.item_id
                        quantity = order_item.quantity

                        item = Item.query.filter_by(item_id=item_id, is_active=1).first()

                        total_amount += quantity * item.unit_price

                        item.available_quantity = item.available_quantity - quantity
                    
                    order.total_amount = total_amount
                    db.session.commit()
            return APIResponse().dump(dict(message='Order is successfully placed.')), 200

        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to place order : {str(e)}')), 400

    pass
            

api.add_resource(PlaceOrderAPI, '/place_order')
docs.register(PlaceOrderAPI)

class ListOrdersByCustomerAPI(MethodResource, Resource):
    @doc(description='List Orders by Customer API', tags=['List Order API'])
    @marshal_with(ListOrderResponse)  # marshalling
    def get(self, **kwargs):
        try:
            if session['user_id']:
                user_id = session['user_id']
                user_type = User.query.filter_by(user_id=user_id).first().level

                if user_type  == 0:
                    orders = Order.query.filter_by(user_id=user_id, is_active=1)
                    order_list = list()
                    for order in orders:
                        order_items = OrderItems.query.filter_by(order_id=order.order_id, is_active=1)
                        
                        order_dict = dict()
                        order_dict['order_id'] = order.order_id
                        order_dict['items'] = list()
                        
                        for order_item in order_items:
                            order_item_dict = dict()
                            order_item_dict['item_id'] = order_item.item_id
                            order_item_dict['quantity'] = order_item.quantity
                            order_dict['items'].append(order_item_dict)
                        
                        order_list.append(order_dict)
                        
            return ListOrderResponse().dump(dict(orders=order_list)), 200
        
        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to list orders : {str(e)}')), 400

    pass
            

api.add_resource(ListOrdersByCustomerAPI, '/list_orders')
docs.register(ListOrdersByCustomerAPI)


class ListAllOrdersAPI(MethodResource, Resource):
    @doc(description='List All Orders API', tags=['List Order API'])
    @marshal_with(ListOrderResponse)  # marshalling
    def get(self, **kwargs):
        try:
            if session['user_id']:
                user_id = session['user_id']
                user_type = User.query.filter_by(user_id=user_id).first().level
                print(user_id)

                if user_type  == 2:
                    orders = Order.query.filter_by(is_active=1)
                    order_list = list()
                    for order in orders:
                        order_items = OrderItems.query.filter_by(order_id=order.order_id, is_active=1)
                        
                        order_dict = dict()
                        order_dict['order_id'] = order.order_id
                        order_dict['items'] = list()
                        
                        for order_item in order_items:
                            order_item_dict = dict()
                            order_item_dict['item_id'] = order_item.item_id
                            order_item_dict['quantity'] = order_item.quantity
                            order_dict['items'].append(order_item_dict)

                        order_list.append(order_dict)
                        
            return ListOrderResponse().dump(dict(orders=order_list)), 200   

        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to list all orders : {str(e)}')), 400

    pass
            
api.add_resource(ListAllOrdersAPI, '/list_all_orders')
docs.register(ListAllOrdersAPI)