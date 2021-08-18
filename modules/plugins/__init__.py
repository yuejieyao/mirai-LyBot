import os
from importlib import import_module


ignore = ["__init__.py", "__pycache__"]
for plugin in os.listdir(__path__[0]):
    if plugin in ignore:
        continue
    try:
        """
        加载plugins目录下的插件
        插件文件要求为插件1级目录下的__init__.py(类名需和文件夹名相同)
        或plugins目录下的文件名非__init__的py文件
        """
        if os.path.isdir(os.path.join(__path__[0], plugin)):
            import_module(f'modules.plugins.{plugin}')
            print(f'添加插件成功: modules.plugins.{plugin}')
        else:
            import_module(f"modules.plugins.{plugin.split('.')[0]}")
            print(f"添加插件成功: modules.plugins.{plugin.split('.')[0]}")
    # except ModuleNotFoundError:
    #     print('插件添加失败: ModuleNotFoundError')
    except Exception as e:
        print(f'插件添加失败:{plugin}')
        print(e)
