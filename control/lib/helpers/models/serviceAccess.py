# coding: utf-8

import logging

from sqlalchemy.orm import join
from sqlalchemy.sql import and_, or_, not_, null
from sqlalchemy.orm.exc import NoResultFound
import datetime

#import ..meta as meta
from ..meta import Session as S
from ..customerService import CustomerService
from ..customerServiceDomain import CustomerServiceDomain
from ..customerServiceChoosenParam import CustomerServiceChoosenParam
from ..customerServiceHistory import CustomerServiceHistory
from ..customerServiceParamHistory import CustomerServiceParamHistory
from ..service import Service
from ..serviceType import ServiceType
from ..serviceParam import ServiceParam
from ..serviceParamType import ServiceParamType
from ..serviceParamValue import ServiceParamValue
from lib.exceptions.programmingException import ProgrammingException
from lib.exceptions.serviceAccessException import ServiceAccessException
log = logging.getLogger(__name__)


class ServiceAccess:

    def __init__(self):
        pass

    def delete_customer_service(self, customer, customer_service_id):
        """
        Deletes customer_service and closes history

        Can raise ServiceAccessException
        """
        if customer is None or customer_service_id is None:
            raise ProgrammingException(1, 'Some of delete_customer_service() \
            parameters are missing!')
        
        service_q = (S.query(CustomerService).filter(
               and_(CustomerService.id==customer_service_id,
                    CustomerService.deleted==False,
                    CustomerService.customer_id==customer.id)))

        if service_q.one().change == True:
             raise ServiceAccessException(2, 'Customer\'s service can\'t be \
             deleted now because it in change state!')

        temp_now = self.__now()
        (service_q.update({ 
            'deleted': True, 
            'change': True,
            }))

        # history for deleted service has to be close immediately
        # because customer can pay no longer 
        # close all not closed yet active entries in hisory
        # normally there should be one but just in case
        close = (S.query(CustomerServiceHistory).filter(
                and_(CustomerServiceHistory.customer_service_id 
                    ==customer_service_id,
                    CustomerServiceHistory.active_to==null()
                    )).update({'active_to': temp_now}))
        
        S.commit()

        return 0

    def services_to_change(self):
        """
        Returns list of customer services ids in change state
        """
        services = []
        for i in (S.query(CustomerService.id).filter(
            CustomerService.change==True)):
            services.append(i.id)
        return services


    def update_changes(self, customer_service_id):
        
        if customer_service_id is None:
            raise ProgrammingException(1, 'No customer_service_id is given')

        temp_now = self.__now()
        customer_service = (S.query(CustomerService).filter(
                CustomerService.id==customer_service_id))
        choosen_params_q = S.query(CustomerServiceChoosenParam).filter(
                CustomerServiceChoosenParam.customer_service_id==customer_service_id)

        shistory = CustomerServiceHistory()
        
        # close all not closed yet active entries in hisory
        # normally there should be one but just in case
        close = (S.query(CustomerServiceHistory).filter(
                and_(CustomerServiceHistory.customer_service_id
                    ==customer_service_id,
                    CustomerServiceHistory.active_to==null()
                    )).update({'active_to': temp_now}))
            

        (customer_service.update({
            'change': False,
            }))

        #make a new history if servcie is not deleted
        if customer_service.one().deleted == False:
            shistory.customer_service_id = customer_service_id
            shistory.active_from = temp_now
            shistory.price = customer_service.one().price

            # update values in db takin coresponding form_values
            for param in choosen_params_q:
                phistory = CustomerServiceParamHistory()
                phistory.service_param_id = param.service_param_id
                phistory.service_param_value_id = param.service_param_value_id
                phistory.price = param.price
                shistory.customer_service_param_history.append(phistory)

            S.add(shistory)


        S.commit()
        return 0



    def save_changes(self, customer, form_result, service_type, customer_service_id):
        """
        Save changes for customer_service in DB

        throws ServiceAccessException
        """
        if (customer is None or form_result is None or
                service_type is None or customer_service_id is None):
            raise ProgrammingException(1, 'Some of save_changes() parameters \
                    are missing!')

        temp_now = self.__now()
        #TODO - get service type from db 
        app_option = self.get_service(service_type)
        
        service_q = (S.query(CustomerService).filter( 
               and_(CustomerService.id==customer_service_id, 
                    CustomerService.deleted==False, 
                    CustomerService.customer_id==customer.id)))

        domain_q = (S.query(CustomerServiceDomain).filter( 
                CustomerServiceDomain.customer_service_id 
                    ==customer_service_id))
        
        if service_q.one().change == True:
            raise ServiceAccessException(2, 'Item can\'t updated because it is \
                    in change state!')
        

        if form_result['active'] is False:
            active_to = temp_now 
        else:
            active_to = None

        (service_q.update({ 
            'customer_description': form_result['description'],
            'price': app_option['service_price'],
            'change': True,
            }))
        (domain_q.update({
            'fqdn': form_result['domain'],
            }))

        # update values in db takin coresponding form_values
        for k, v in form_result.items():
            
            if k in app_option['params'].keys():
                param_q = (S.query(CustomerServiceChoosenParam).filter(
                        and_(
                            CustomerServiceChoosenParam.customer_service_id
                            ==customer_service_id,
                            CustomerServiceChoosenParam.service_param_id
                            ==app_option['params'][k]['param_id']
                        )))

                #price - balance param's price and choosen value
                param_price = app_option['params'][k]['param_price']
                pp = S.query(ServiceParamValue.price).get(v)
                param_price += pp[0]

                (param_q.update({
                    'service_param_value_id': v,
                    'price': param_price,
                    }))

        S.commit()
        return 0

    
    def save_new(self, customer, form_result, service_type):

        if customer is None or form_result is None or service_type is None:
            raise ProgrammingException(1, 'Some of save_new parameters are \
                    missing!')

        app_option = self.get_service(service_type)
        temp_now = self.__now()

        service = CustomerService()
        domain = CustomerServiceDomain()
                
        # zapisujemy w tabeli CustomerService
        # id klienta, opis dla aplikacji, czy jest aktywna
        # oraz cene
        service.customer_id = customer.id
        service.service_id = app_option['service_id']
        service.customer_description = form_result['description']

        #cena uslugi dla klienta - bez parametrow i wartosci
        service.price = app_option['service_price']
        #dodajemy do sesji

        # dla danych z fromularza sprawdzamy ktore sa odpowiednikami
        # parametrow uslug znajdujacych sie w bazie i uzyskujemy dla nich
        # id w tabeli
        for k, v in form_result.items():
            
            if k in app_option['params'].keys():
                params = CustomerServiceChoosenParam()
                params.service_param_id = app_option['params'][k]['param_id']

                # przypisz id tabeli wartosci parametrow - dane z
                # formularza
                params.service_param_value_id = v
                
                #cena - suma dla parametru i wybranej wartosci
                params.price = app_option['params'][k]['param_price']
                param_price = S.query(ServiceParamValue.price).get(v)
                params.price += param_price[0]

                service.customer_service_choosen_param.append(params)

        domain.fqdn = form_result['domain']
        service.customer_service_domain.append(domain)

        S.add(service)
        S.commit()

        return 0


    def get_service(self, service_type):
        """
        {'params': {
            u'Cages': {'name': u'Cages',
                       'param_id': 7,
                       'param_price': 0.0,
                       'values': [(10, u'1', u'1 cage'),
                                  (25, u'2', u'2 cages'),
                                  (24, u'3', u'3 cages'),
                                  (26, u'4', u'4 cages'),
                                  (19, u'5', u'5 cages'),
                                  (18, u'6', u'6 cages'),
                                  (5, u'7', u'7 cages'),
                                  (16, u'8', u'8 cages'),
                                  (1, u'9', u'9 cages'),
                                  (20, u'10', u'10 cages'),
                                  (8, u'11', u'11 cages'),
                                  (21, u'12', u'12 cages'),
                                  (11, u'13', u'13 cages')]},
            u'Database': {'name': u'Database',
                          'param_id': 2,
                          'param_price': 0.0,
                          'values': [(4, u'1.0', u'1 GB'),
                                     (27, u'2.5', u'2,5 GB')]},
            u'Framework': {'name': u'Framework',
                           'param_id': 4,
                           'param_price': 0.0,
                           'values': [(7, u'Pylons 0.96', u'Pylons 0.96'),
                                      (23, u'Pylons 1.1', u'Pylons 1.1')]},
            u'Memory': {'name': u'Memory',
                        'param_id': 1,
                        'param_price': 0.0,
                        'values': [(6, u'40', u'40 MB'),
                                   (12, u'80', u'80 MB'),
                                   (9, u'120', u'120 MB')]},
            u'Space': {'name': u'Space',
                       'param_id': 5,
                       'param_price': 0.0,
                       'values': [(22, u'150.0', u'150 MB'),
                                  (2, u'250.0', u'250 MB')]}},
         'service_id': 1,
         'service_price': 0.05
        }

        """
        ret_service = {}    
        tmp = {}
        service = S.query(Service).join( ServiceType \
                    ).filter(and_(ServiceType.type==service_type, \
                        or_(Service.available_to<=datetime.datetime.now(), \
                        Service.available_to==null() ) \
                        )).first()

        ret_service['service_id'] = service.id
        ret_service['service_price'] = service.price

        for service_param in S.query(ServiceParam).filter( \
                and_(ServiceParam.service_id==service.id, \
                ServiceParam.available_to==null())).order_by(\
                ServiceParam.sort_order):

            tmp[service_param.name] = { \
                    'name': service_param.name,
                    'param_id': service_param.id,
                    'param_price': service_param.price,
                    'values': (S.query(ServiceParamValue.id, 
                            ServiceParamValue.value, ServiceParamValue.name, 
                            ServiceParamValue.price).filter( 
                            ServiceParamValue.service_param_id==service_param.id
                            ).order_by(ServiceParamValue.sort_order).all()),
                    }

        ret_service['params'] = tmp

        return ret_service

    def get_customer_service(self, customer_service_id):
 
        """
        Example returned value


        {'active': False,
         'change': False,
         'domain': u'http://wojtek.pl',
         'params': {u'cage': {
                            'value': u'7', 
                            'value_id': 7},
                   'db': {
                            'value': u'2.5',
                            'value_id': 18},
                 'framework': {
                            'value': u'Django 1.3', 
                            'value_id': 22},
                 'hdd': {
                            'value': u'150.0', 
                            'value_id': 19},
                 'ram': {   
                            'value': u'80', 
                            'value_id': 15}},
                 'service': <panelklienta.model.customerService.CustomerService object at 0xa9131ec>}
        
        raises ServiceAccessException
        """
        ret_service = {}
        tmp = {}
        if customer_service_id is None:
            service = CustomerService()
        else:
            try:
                service = (S.query(CustomerService).filter( and_(
                        CustomerService.deleted==False,
                        CustomerService.id==customer_service_id)).one())
            except NoResultFound:
                raise ServiceAccessException(2, 'Item doesn\'t \
                exist or has been deleted!')
            else:
                ret_service['service'] = service

        ret_service['change'] = service.change

        if customer_service_id is None:
            tmp['hdd'] = {'value_id': '', 'value': ''}
        else:
            for param in (S.query(CustomerServiceChoosenParam).filter(
                    CustomerServiceChoosenParam.customer_service_id==customer_service_id)):

                tmp[S.query(ServiceParam.name).get(param.service_param_id).name] = {
                        'value_id': param.service_param_value_id,
                        'value': (S.query(ServiceParamValue 
                                ).get(param.service_param_value_id).value) ,
                        }
        ret_service['params'] = tmp

        if customer_service_id is None:
            ret_service['domain'] = ''
        else:
            ret_service['domain'] = ( S.query(CustomerServiceDomain.fqdn).filter( 
                    CustomerServiceDomain.customer_service_id==customer_service_id
                    ).first().fqdn )
        
        return ret_service


    def __now(self):
        return datetime.datetime.now()
