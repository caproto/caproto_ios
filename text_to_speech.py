#!/usr/bin/env python3
import caproto
from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run
import time
import speech


class SpeechIOC(PVGroup):
    language = pvproperty(value=['English'],
                          doc='Language to use',
                          dtype=caproto.ChannelType.ENUM,
                          enum_strings=list(speech.get_languages()),
                          string_encoding='utf-8')
    speak = pvproperty(value=['text'],
                       doc='Text to speak',
                       string_encoding='utf-8')
    rate = pvproperty(value=[1.0],
                      doc='Normalized speech rate')
    speaking = pvproperty(value=[0])

    @speak.putter
    async def speak(self, instance, value):
        if isinstance(value, (list, tuple)):
            value, = value
        language = self.language.value[0]
        rate = self.rate.value[0]
        print(f'Saying {value!r} in language {language} at rate {rate}')
        speech.say(value, language=language, rate=rate)

    @speaking.startup
    async def speaking(self, instance, async_lib):
        while True:
            await self.speaking.write(value=[speech.is_speaking()])
            await async_lib.library.sleep(0.1)


if __name__ == '__main__':
    ioc_options, run_options = ioc_arg_parser(
        default_prefix='speech:',
        desc="Text-to-speech IOC")
    ioc = SpeechIOC(**ioc_options)
    run(ioc.pvdb, **run_options)
