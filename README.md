# lot51/core-library

Core Library is a collection of useful snippets and tunables for The Sims 4 mods! It's recommended to use it as a dependency to help prevent many injections to common game methods. 

## Usage

Download the latest packaged ts4script from https://lot51.cc/core and place in your Mods folder.

## Create a Logger

```py
from lot51_core.utils.log import Logger
from lot51_core.utils.paths import get_mod_root
from lot51_core.utils.config import Config


# Get the mod root relative to this file.
# By default will traverse up 2 parent directories to handle ts4scripts
mod_root = get_mod_root(__file__, depth=2)

# Create a logger that outputs in mod root
logger = Logger("NameOfYourMod", mod_root, "my_mod.log", version="1.0")
```

## Create a Config file

```py
# Create a json config file in mod root
config = Config(mod_root, "my_mod.json", logger, default_data={"custom_setting": False})

# Get a value, and provide a default return value if the setting does not exist
custom_setting = config.get("custom_setting", default=False)

# Set a value in memory and then save. Useful for multiple operations
config.set("custom_setting", True)
config.set("custom_setting_2", True)
config.save()

# Set a value and save it to the json file immediately
config.set_hard("custom_setting", True)
```

## Replace your injections with event handlers

A context object will be passed to most events that provide common game state values.

### Event Handler

All exceptions will be caught and automatically written to lot51_core.log

```py
from lot51_core.services.events import event_handler


@event_handler('zone.load')
def _on_zone_load(*args, context=None, **kwargs):

    # returns a DateAndTime of the currently simulated time internally
    sim_now = context.sim_now

    # returns a DateAndTime of the time displayed in the UI
    # representing the time the game should be simulating to.
    game_now = context.game_now

    # Returns true/false
    in_world_edit_mode = context.in_world_edit_mode
    is_traveling = context.is_traveling

    # Returns the current save slot id, this does not change
    # when the game switches to a scratch save so you can use it for
    # persisting data per save
    save_slot_id = context.save_slot_id

    # Returns the name of the current save as a string
    save_slot_name = context.save_slot_name

    logger.debug("zone has loaded")
```


### Events
 
*\* denotes an event that receives the context object above as a kwarg*

- `game.setup` *
- `global_service.start`
- `game_services.started` (after all custom services started)
- `game.load` *
- `zone.load` *
- `zone.all_households_and_sim_infos_loaded` *
- `zone.cleanup_objects` *
- `zone.loading_screen_lifted` *
- `game.update` * (warning: this is called on every game tick, only use if you know what you're doing)
- `game.pre_save` *
- `game.save` *
- `zone.unload` *
- `global_service.stop`

- `build_buy.enter` *
- `build_buy.exit` *

## Register a custom Game Service

```py
from sims4.service_manager import Service
from lot51_core.services.service_manager import service_manager


class MyCustomService(Service):

    def save(self, *args, **kwargs):
        pass

    def pre_save(self, *args, **kwargs):
        pass

    def setup(self, *args, **kwargs):
        pass

    def load(self, *args, **kwargs):
        pass

    def start(self, *args, **kwargs):
        pass

    def stop(self, *args, **kwargs):
        pass

    def on_zone_load(self, *args, **kwargs):
        pass

    def on_zone_unload(self, *args, **kwargs):
        pass

    def on_cleanup_zone_objects(self, *args, **kwargs):
        pass

    def on_all_households_and_sim_infos_loaded(self, *args, **kwargs):
        pass


# Register your custom service
service_manager.register_service(MyCustomService)
```

## License

MIT License

Copyright (c) 2022 Lot 51

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
