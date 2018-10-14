#!/usr/bin/env python3
from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run
import time
import photos
import numpy as np


image_width, image_height = 1024, 1024


class CameraIOC(PVGroup):
    acquire = pvproperty(value=[0],
                         doc='Process to acquire an image',
                         mock_record='bo')
    image = pvproperty(value=[0] * (image_width * image_height),
                       doc='Image data')

    @acquire.putter
    async def acquire(self, instance, value):
        image = photos.capture_image()
        # resize to (width, height)
        print(image)
        image = image.resize((image_width, image_height))
        print(image, np.asarray(image).shape)
        # and convert to grayscale
        image_array = np.dot(np.asarray(image)[..., :3], [0.299, 0.587, 0.114])
        await self.image.write(image_array.flatten().astype(np.uint32))


if __name__ == '__main__':
    ioc_options, run_options = ioc_arg_parser(
        default_prefix='motion:',
        desc="iOS camera IOC")
    ioc = CameraIOC(**ioc_options)
    run(ioc.pvdb, **run_options)
