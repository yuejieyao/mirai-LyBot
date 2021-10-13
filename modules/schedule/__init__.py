from importlib import import_module
from modules.utils import log as Log
import traceback
import os


ignore = ["__init__.py", "__pycache__"]
for plugin in os.listdir(__path__[0]):
    if plugin in ignore:
        continue
    try:
        """
        加载此目录下的定时插件
        插件文件要求为插件1级目录下的__init__.py
        或plugins目录下的文件名非__init__的py文件
        """
        if os.path.isdir(os.path.join(__path__[0], plugin)):
            import_module(f'modules.schedule.{plugin}')
            Log.info(msg=f'schedule register success : {plugin}')
        else:
            name = plugin.split('.')[0]
            import_module(f"modules.schedule.{name}")
            if name != 'miraiSchedule':
                Log.info(msg=f'schedule register success : {name}')
    except Exception:
        Log.info(msg=f'schedule register failed : {plugin}')
        Log.error(msg=traceback.format_exc())
