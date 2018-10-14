#!/usr/bin/env python3
import caproto
from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run
import speech
import sound


class VoiceRecognitionIOC(PVGroup):
    duration = pvproperty(value=[5.0],
                          doc='Duration to listen')
    start = pvproperty(value=[0],
                       doc='Start listening')
    confidence = pvproperty(value=[0.],
                            doc='Recognition confidence')
    text = pvproperty(value=['text'],
                      doc='Spoken text',
                      string_encoding='utf-8',
                      dtype=caproto.ChannelType.STRING)
    # TODO: change to CHAR when newer caproto is tagged

    @start.startup
    async def start(self, instance, async_lib):
        self.async_lib = async_lib.library

    @start.putter
    async def start(self, instance, value):
        duration, = self.duration.value

        rec = sound.Recorder('recorded.m4a')
        rec.record()
        print(f'Recording for {duration}...')
        await self.async_lib.sleep(duration)
        rec.stop()
        await self.async_lib.sleep(0.1)
        result = speech.recognize('recorded.m4a')
        if len(result):
            full_text, full_info = result[0]
            await self.text.write([full_text])
            await self.confidence.write([min(info['confidence']
                                             for info in full_info)])
            for info in full_info:
                print('@ {timestamp} {duration} sec'
                      'heard: {substring} ({confidence})'
                      ''.format(**info))

        else:
            await self.text.write([str(result)])


if __name__ == '__main__':
    ioc_options, run_options = ioc_arg_parser(
        default_prefix='speech:',
        desc="Spoken word to PV")
    ioc = VoiceRecognitionIOC(**ioc_options)
    run(ioc.pvdb, **run_options)
