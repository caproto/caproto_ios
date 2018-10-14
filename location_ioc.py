#!/usr/bin/env python3
import caproto
from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run
import time
import location


class LocationIOC(PVGroup):
    authorized = pvproperty(value=[0],   # enum TODO
                            doc='Authorized access to location data')
    coordinates = pvproperty(value=[0., 0.],   # enum TODO
                             doc='Latitude, longitude')
    location = pvproperty(value=[''],
                          doc='Street address information',
                          max_length=1000,
                          dtype=caproto.ChannelType.CHAR)

    @authorized.startup
    async def authorized(self, instance, async_lib):
        location.start_updates()
        try:
            while True:
                timestamp = time.time()
                if not location.is_authorized():
                    await self.authorized.write(value=[0], timestamp=timestamp)
                else:
                    info = location.get_location()
                    await self.authorized.write(value=[1], timestamp=timestamp)
                    latitude = info.get('latitude', 0.)
                    longitude = info.get('longitude', 0.)
                    timestamp = info.get('timestamp', timestamp)
                    await self.coordinates.write(value=[latitude, longitude],
                                                 timestamp=timestamp)
                    loc = location.reverse_geocode(dict(latitude=latitude,
                                                        longitude=longitude))
                    await self.location.write(value=[str(loc)],
                                              timestamp=timestamp)
                await async_lib.library.sleep(5.0)
        finally:
            location.stop_updates()


if __name__ == '__main__':
    ioc_options, run_options = ioc_arg_parser(
        default_prefix='location:',
        desc="iOS location data IOC")
    ioc = LocationIOC(**ioc_options)
    run(ioc.pvdb, **run_options)
