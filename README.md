# lot51/core-library

Core Library is a collection of useful snippets and tunables for The Sims 4 mods! It's recommended to use it as a dependency to help prevent many injections to common game methods.

## Usage

Download the latest packaged ts4script from https://lot51.cc/core and place in your Mods folder.

If you are creating a mod that depends on this library, please do not include the packaged library with your files. Direct your users to the url above to ensure they receive the latest patch updates.

## Versioning

Core Library follows [Semantic Versioning](https://semver.org/). Given a version number MAJOR.MINOR.PATCH:

- MAJOR version changes represent a change that breaks backwards compatibility
- MINOR version changes represent new/updated functionality that is backwards compatible
- PATCH version changes represent backwards compatible bug fixes

The TuningInjector allows you to set a minimum core version to prevent any game breaking injections, and will notify the Player they have an incompatible version installed. 

It's recommended to set the minimum as a MAJOR.MINOR version to allow your injections to run if a player has a patch version that does not exactly match.

## Snippet TDESCS

These snippets can be generated and included in your packages to use features provided by the library without any scripting. Additional snippets are available in the `snippets` directory but have not yet been documented.

- [TuningInjector](https://lot51.cc/tdesc/Contrib/TuningInjector.tdesc)
- [PurchasePickerSnippet](https://lot51.cc/tdesc/Contrib/PurchasePickerSnippet.tdesc)

## Commands

These commands are available in the cheat box, or as a `do_command` basic extra in an Interaction.

#### lot51_core.open_url \<url\> \<params\>

Opens a URL in the Player's default browser. Params (optional) can be a stringified JSON object with additional url query params.


#### purchase_picker.refresh \<id\>

Forces a refresh of the available stock in a PurchasePickerSnippet that has `stock_management` enabled.


## Create a Logger

```py
from lot51_core.utils.log import Logger
from lot51_core.utils.paths import get_mod_root
from lot51_core.utils.config import Config


# Get the mod root relative to this file.
# By default will traverse up 2 parent directories to handle compiled ts4scripts
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

### GUID Safety

It is recommended to convert 64-bit IDs to a `string` before saving to a config file. Then convert the string back to an `int` when retrieving it.
 The config data is stored in JSON format, and you may experience data loss as 64-bit integer literals are unsupported in certain contexts.


```py
# set
household_id = services.active_household_id()
config.set("saved_household_id", str(household_id))

# get
household_id = int(config.get("saved_household_id", 0))
```

## Replace your injections with event handlers

Many mods rely on code running when the loading screen lifts, or when a Sim travels. As players grow their script mod collection they may find that their game is unable to load due to core game functions having too many injections. Python has a Maximum Recursion Depth that prevents functions from being wrapped more than 1000 times. 

Core event handlers can replace most injection points and support a near unlimited amount of listeners. Additionally:

- All exceptions will automatically be caught and written to `lot51_core.log`.
- A `context` object will be passed to most events that provides common game state values.

### Event Handler

```py
from lot51_core.services.events import event_handler, CoreEvent


@event_handler(CoreEvent.ZONE_LOAD)
def _on_zone_load(service, context=None, **kwargs):

    # Returns a DateAndTime of the currently simulated time internally. 
    # This value will always be <= to game_now
    sim_now = context.sim_now

    # Returns a DateAndTime of the time displayed in the UI
    # representing the time the game should be simulating to.
    # This value will always be >= to sim_now
    game_now = context.game_now

    # Returns true/false
    in_world_edit_mode = context.in_world_edit_mode
    is_traveling = context.is_traveling

    # Returns the current save slot id, this does not change
    # when the game switches to a scratch save, so you can 
    # use it for persisting data per save
    save_slot_id = context.save_slot_id

    # Returns the name of the current save as a string
    save_slot_name = context.save_slot_name

    logger.debug("zone has loaded")
```


### Core Events

Most events mirror methods called by game services, with additional events provided by injections.

Events are generally listed in the order they are called. Use the CoreEvent enum as a shortcut for event names.

*\* An asterisk denotes an event that receives the context object as a kwarg*

#### instance_managers.loaded

Called after all instance managers have loaded. You can perform tuning injections here.

#### global_service.start

The Core Library global service has been set up and started.

#### game_services.started

All custom Service classes have been registered.

#### game.setup *

Called when the game has initialized all game services and is setting them up before starting them.

#### game.load *

Raw save game data is being loaded into services to prepare for zone load.

#### zone.load *

The zone instance is now available. No sims or objects are available yet if this is during the initial launch of the game rather than traveling.

####  zone.all_households_and_sim_infos_loaded *

The household and sim info managers have been loaded. This is only called once on the initial load of the save.

#### zone.cleanup_objects *

At this point all Sims and objects have been spawned into the zone behind the loading screen and can be modified before the Player can see them.

#### zone.loading_screen_lifted *

The zone is fully loaded and the loading screen has disappeared. This is the best time to display startup notifications.

#### game.pre_save *

Services are preparing to save the game.

#### game.save *

Services are now saving data into the protobufs. The zone is still available.

#### zone.unload *

The zone is being destroyed for travel or exit. Most services will be unavailable after this point.

#### global_service.stop *

The Core Library global service has been stopped.

#### game_object.added

A GameObject has been spawned into the world. The obj instance is provided as the 2nd argument.

#### game_object.destroyed

A GameObject has been removed from the world. The obj instance is provided as the 2nd argument.

#### build_buy.enter *

Called when the Player has entered build mode

#### build_buy.exit *

Called when the Player has exited build mode. Useful to detect lot trait changes, or new objects.


#### game.update *

This event is useful for creating your own loops based on the server clock as an alternative to alarms. You can even check the difference between game_now and sim_now to detect a large time jump and prevent your mod from clogging the simulation while it catches up. (Generally a jump greater than 30 minutes indicates simulation lag or a player cheating the time forward and your update method should bail out.)

Warning: The simulation and client are single threaded and this event is broadcast on every server tick. Blocking the game loop, or executing long-running code on every tick can cause the game client to completely crash without the ability to generate any LastException files. 

---

This example is a custom service class that will update every 15 sim minutes, unless the simulation threshold has been met.
```py
from date_and_time import TimeSpan, create_time_span
from lot51_core.services.events import event_handler, CoreEvent
from lot51_core import logger

class SomeCustomService:
    UPDATE_INTERVAL = 15
    SIMULATION_THRESHOLD = 30
    
    def __init__(self):
        self._next_update = TimeSpan.ZERO
        
    def can_update(self, context):
        if not self.time_jump_detected(context):
            if self._next_update == TimeSpan.ZERO or context.sim_now >= self._next_update:
                return True
    
    def time_jump_detected(self, context):
        diff = context.game_now - context.sim_now
        if diff.in_minutes() >= self.SIMULATION_THRESHOLD:
            return True
    
    def update(self, context):
        if not self.can_update(context):
            return
        self._next_update = context.sim_now + create_time_span(minutes=self.UPDATE_INTERVAL)
        
        # DO SOMETHING HERE EVERY FIFTEEN MINUTES
        logger.debug("4 8 15 16 23 42")

some_custom_service = SomeCustomService()

@event_handler(CoreEvent.GAME_TICK)
def _my_custom_service_update_handler(*args, context=None):
    # check if the zone is available
    if context.zone is not None:
        some_custom_service.update(context)
```

Exceptions in the handler will automatically be caught and logged to `lot51_core.log` as a safeguard to a simulation crash. This usually presents itself as Sims replaying the same animation constantly, walk to their destination and then standing forever, and pie menus not opening. It can sometimes recover by waiting, or opening/closing the ESC menu. Otherwise players will need to force quit the game. 

Socket based loops like an HTTP/TCP server should use this event to read AND write in the same thread. Executing code from a separate thread can cause the game client to immediately crash when it attempts to run functions that have been imported from EA's C code.


### Custom Events

You may also use the event service to broadcast your own events. Please do not use the reserved event names above. Prefix your events with your creator or mod name to ensure you don't conflict with other creators.

The EventService instance will be provided as the first arg to easily broadcast additional events or responses. Additionally, all parameters passed to `process_event` will pass through to the handler.

```py
from lot51_core.services.events import event_service, event_handler

event_service.process_event("my_mod.do_something", additional_data=(1, 2, 3))

@event_handler("my_mod.do_something")
def do_something_handler(service, additional_data=()):
    pass
```

## Register a custom Game Service

Core Library has an alternative manager to help register "official" services in the game's ServiceManager.

Note: Services are still initialized when entering a zone from world edit mode. It's recommended to check the `in_world_edit_mode` boolean on the context object.  

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

# A helper function to get your service instance
def get_my_service():
    return service_manager.get_service(MyCustomService)
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
