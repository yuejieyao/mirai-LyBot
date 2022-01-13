import os
import traceback
from importlib import import_module
from modules.utils import log as Log


ignore = ["__init__.py", "__pycache__"]
for event in os.listdir(__path__[0]):
    if event in ignore:
        continue
    try:
        """
        加载events目录下的插件
        插件文件要求为插件1级目录下的__init__.py(类名需和文件夹名相同)
        或events目录下的文件名非__init__的py文件
        """
        if os.path.isdir(os.path.join(__path__[0], event)):
            import_module(f'modules.events.{event}')
            Log.info(msg=f'event register success : {event}')
        else:
            name = event.split('.')[0]
            import_module(f"modules.events.{name}")
            if name != 'miraiEvent':
                Log.info(msg=f"event register success : {name}")
    except Exception:
        Log.info(msg=f'event register failed : {event}')
        Log.error(msg=traceback.format_exc())
