# -*- coding: utf-8 -*-
import redis
from app.config import Config


r_conf = Config.REDIS_CONFIG
r = redis.Redis(**r_conf)

