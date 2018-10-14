#!/usr/bin/env python3
from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run
import time
import motion


class MotionIOC(PVGroup):
    gravity = pvproperty(value=[0., 0., 0.],
                         doc='x, y, z')
    user_acceleration = pvproperty(value=[0.])
    attitude = pvproperty(value=[0., 0., 0.],
                          doc='roll, pitch, yaw')
    magnetic_field = pvproperty(value=[0., 0., 0., 0.],
                                doc='X, Y, Z, accuracy')

    @gravity.startup
    async def gravity(self, instance, async_lib):
        motion.start_updates()
        try:
            while True:
                timestamp = time.time()
                gravity = motion.get_gravity()
                user_acceleration = motion.get_user_acceleration()
                attitude = motion.get_attitude()
                magnetic_field = motion.get_magnetic_field()
                await self.gravity.write(value=gravity, timestamp=timestamp)
                await self.user_acceleration.write(value=user_acceleration,
                                                   timestamp=timestamp)
                await self.attitude.write(value=attitude, timestamp=timestamp)
                await self.magnetic_field.write(value=magnetic_field,
                                                timestamp=timestamp)
                await async_lib.library.sleep(0.01)
        finally:
            # TODO: put in @gravity.shutdown when in released version
            motion.stop_updates()


if __name__ == '__main__':
    ioc_options, run_options = ioc_arg_parser(
        default_prefix='motion:',
        desc="iOS motion sensor data IOC")
    ioc = MotionIOC(**ioc_options)
    run(ioc.pvdb, **run_options)
