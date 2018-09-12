import logging
import sys

import fakeredis
import rq_dashboard
import structlog
from flask import Flask
from flask_redis import FlaskRedis
from structlog.processors import (JSONRenderer, StackInfoRenderer, TimeStamper,
                                  format_exc_info)
from structlog.stdlib import add_log_level, add_logger_name, filter_by_level

import easyq.api.metrics as metrics
import easyq.api.rqb as rqb
from easyq.api.enqueue import bp as enqueue
from easyq.api.healthcheck import bp as healthcheck
from easyq.api.task import bp as task_api
from easyq.models import db


class Application:
    def __init__(self, config, log_level, testing=False):
        self.config = config
        self.log_level = log_level
        self.create_app(testing)

    def create_app(self, testing):
        self.app = Flask('easyq')
        self.app.testing = testing
        self.app.config.from_object(rq_dashboard.default_settings)
        self.app.config.update(self.config.items)
        self.app.config.DEBUG = self.config.DEBUG
        self.app.config.ENV = self.config.ENV
        self.app.original_config = self.config
        self.app.log_level = self.log_level
        self.configure_logging()
        self.connect_redis()
        self.connect_queue()
        self.connect_db()
        self.load_executor()

        metrics.init_app(self.app)
        self.app.register_blueprint(metrics.bp)
        self.app.register_blueprint(healthcheck)
        self.app.register_blueprint(enqueue)
        self.app.register_blueprint(task_api)
        self.app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")

    def configure_logging(self):
        if self.app.testing:
            structlog.reset_defaults()

        disabled = [
            'docker.utils.config',
            'docker.auth',
            'docker.api.build',
            'docker.api.swarm',
            'docker.api.image',
            'rq.worker',
            'werkzeug',
            'requests',
            'urllib3',
        ]

        for logger in disabled:
            log = logging.getLogger(logger)
            log.setLevel(logging.ERROR)
            log.disabled = True
        self.app.logger.disabled = True

        logging.basicConfig(
            level=self.log_level, stream=sys.stdout, format="%(message)s")

        chain = [
            filter_by_level,
            add_log_level,
            add_logger_name,
            TimeStamper(fmt="iso"),
            StackInfoRenderer(),

            format_exc_info,
            JSONRenderer(indent=1, sort_keys=True),
        ]

        log = structlog.wrap_logger(
            logging.getLogger(__name__),
            processors=chain,
            context_class=dict,
            wrapper_class=structlog.stdlib.BoundLogger,
            # cache_logger_on_first_use=True,
        )
        self.logger = log
        self.app.logger = self.logger

    def connect_redis(self):
        self.logger.debug('Connecting to redis...')

        if self.app.testing:
            self.app.redis = FlaskRedis.from_custom_provider(
                fakeredis.FakeStrictRedis)
            self.app.redis.connect = self._mock_redis(True)
            self.app.redis.disconnect = self._mock_redis(False)
        else:
            self.app.redis = FlaskRedis()

        self.logger.info('Connection to redis successful')
        self.app.redis.init_app(self.app)

    def connect_queue(self):
        self.app.queue = None
        self.app.register_blueprint(rqb.bp)
        rqb.init_app(self.app)

    def connect_db(self):
        db.init_app(self.app)

    def load_executor(self):
        '''Can't be loaded eagerly due to fork of jobs'''

        def _loads():
            if getattr(self.app, 'executor_module', None) is None:
                executor_module = __import__(self.config.EXECUTOR)

                if '.' in self.config.EXECUTOR:
                    for part in self.config.EXECUTOR.split('.')[1:]:
                        executor_module = getattr(executor_module, part)

                self.app.executor_module = executor_module

            return self.app.executor_module.Executor(self.app)

        self.app.load_executor = _loads

    def run(self, host, port):
        self.app.run(host, port)

    def _mock_redis(self, connected):
        def handle():
            self.app.redis._redis_client.connected = connected

        return handle