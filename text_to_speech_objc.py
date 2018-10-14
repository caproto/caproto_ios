#!/usr/bin/env python3
import caproto
from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run
import speech

from objc_util import ObjCClass

AVSpeechUtterance = ObjCClass('AVSpeechUtterance')
AVSpeechSynthesizer = ObjCClass('AVSpeechSynthesizer')
AVSpeechSynthesisVoice = ObjCClass('AVSpeechSynthesisVoice')


class SpeechIOC(PVGroup):
    language = pvproperty(value=['en-US'],
                          doc='Language to use',
                          dtype=caproto.ChannelType.ENUM,
                          enum_strings=list(speech.get_languages()),
                          string_encoding='utf-8')
    speak = pvproperty(value=['text'],
                       doc='Text to speak',
                       string_encoding='utf-8')
    rate = pvproperty(value=[0.5],
                      doc='Normalized speech rate')
    speaking = pvproperty(value=[0])

    @speak.startup
    async def speak(self, instance, async_lib):
        self.voices = AVSpeechSynthesisVoice.speechVoices()
        self.synthesizer = AVSpeechSynthesizer.new()

    @speak.putter
    async def speak(self, instance, value):
        if isinstance(value, (list, tuple)):
            value, = value

        language = self.language.value[0]
        voice = AVSpeechSynthesisVoice.voiceWithLanguage_(language)
        for voice in self.voices:
            print(voice)
            if 'Enhanced' in str(voice.description()):
                break

        self.voice = voice
        utterance = AVSpeechUtterance.speechUtteranceWithString_(value)
        rate = self.rate.value[0]

        utterance.rate = rate
        utterance.voice = self.voice
        utterance.useCompactVoice = False

        print(f'Saying {value!r} in {language} at rate {rate}')
        self.synthesizer.speakUtterance_(utterance)

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
