import os
import logging

from twisted.web import server
from twisted.internet import reactor, endpoints

from lib.conf_tool import http_conf
from lib.interface_manager import InterfaceManager
from lib.log_utils import logging_init
from lib.servers.mgmt_server import MServer
from lib.servers.service_server import SServer


mgmt_host = http_conf.get('http_server', "mgmt_host")
mgmt_port = int(http_conf.get('http_server', "mgmt_port"))

service_host = http_conf.get('http_server', "service_host")
service_port = int(http_conf.get('http_server', "service_port"))

interface_path = os.path.join(os.path.abspath('.'), 'interface')
cron_lib_path = os.path.join(os.path.abspath('.'), 'cron_lib')

reactor.suggestThreadPoolSize(200)


def start_http_service():
    logging_init()

    interface_manager = InterfaceManager(interface_path)
    interface_manager.reload_interface()

    service_site = server.Site(SServer(interface_manager))
    service_endpoint = endpoints.TCP4ServerEndpoint(reactor, port=service_port, interface=service_host)
    service_defer = service_endpoint.listen(service_site)
    service_defer.addCallback(
        lambda result: logging.info("\nService Server started http://%s:%s\n" % (service_host, service_port)))
    service_defer.addErrback(
        lambda result: logging.error("\nService Server Error http://%s:%s %s\n" %
                                     (service_host, service_port, result.getErrorMessage())))

    mgmt_site = server.Site(MServer(interface_manager))
    mgmt_endpoint = endpoints.TCP4ServerEndpoint(reactor, port=mgmt_port, interface=mgmt_host)
    mgmt_defer = mgmt_endpoint.listen(mgmt_site)
    mgmt_defer.addCallback(
        lambda result: logging.info("\nMGMT Server started http://%s:%s\n" % (mgmt_host, mgmt_port)))
    mgmt_defer.addErrback(
        lambda result: logging.error("\nMGMT Server Error http://%s:%s %s\n" %
                                     (mgmt_host, mgmt_port, result.getErrorMessage())))

    reactor.run()

    logging.info("Server stopped.")
