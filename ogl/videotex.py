
import os
import time
from OpenGL.GL import *
import mediadecoder  # For the state constants
from mediadecoder.decoder import Decoder
from pixelbuffer import PixelBuffer
import logging
logger = logging.getLogger("%s" % __name__)

'''
the decoder thread and the clock can get out of sync.
If the renderer is paused, the clock keeps going on,
and the end_func can be called in plain middle.
- to solve.

for short clips, to generate sprites
better read the clip once and generate a texture sequence
'''

class VideoTex():

    def __init__(_,
                 soundrenderer="pyaudio",
                 media=None,
                 end_func=lambda:None,
                 loop=False,
                 #centered=False,
                 audio=True):
        '''
        end func is triggered when the video reach the end
        (and at each loop)
        '''
        #_.width, _.height = dimensions[0],dimensions[1]
        _.soundrenderer = soundrenderer
        _.loop = loop
        _.texUpdated = False

        _.decoder = Decoder(
            videorenderfunc=_.__texUpdate,
            end_func=end_func
        )

        _.texture_locked = False
        media and _.load_media(media, audio=audio)



    def calc_scaled_res(_, tex_res, vid_res):
        rs = tex_res[0] / float(tex_res[1])
        ri = vid_res[0] / float(tex_res[1])

        if rs > ri:
            return (int(vid_res[0] * tex_res[1] / vid_res[1]), tex_res[1])
        else:
            return (tex_res[0], int(vid_res[1] * tex_res[0] / vid_res[0]))

    def load_media(_, vidSource, audio=True):

        logger.debug('loading %s' % vidSource)
        if not os.path.exists(vidSource):
            raise Exception("File not found: " + vidSource)

        _.decoder.load_media(vidSource, audio)
        _.decoder.loop = _.loop
        _.vidsize = _.decoder.clip.size
        _.width = _.vidsize[0]
        _.height = _.vidsize[1]
        _.__textureSetup()


        if(_.decoder.audioformat):
            if _.soundrenderer == "pygame":
                from mediadecoder.soundrenderers import SoundrendererPygame
                _.audio = SoundrendererPygame(_.decoder.audioformat)
            elif _.soundrenderer == "pyaudio":
                from mediadecoder.soundrenderers.pyaudiorenderer import SoundrendererPyAudio
                _.audio = SoundrendererPyAudio(_.decoder.audioformat)
            elif _.soundrenderer == "sounddevice":
                from mediadecoder.soundrenderers.sounddevicerenderer import SoundrendererSounddevice
                _.audio = SoundrendererSounddevice(_.decoder.audioformat)
            _.decoder.set_audiorenderer(_.audio)

        _.play()



    def __textureSetup(_):
        glEnable(GL_TEXTURE_2D)
        glMatrixMode(GL_MODELVIEW)
        _.id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, _.id)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB,
                     _.vidsize[0], _.vidsize[1], 0,
                     GL_RGB, GL_UNSIGNED_BYTE, None)
        _.tex_coords = (0,1,0, 1,1,0, 1,0,0, 0,0,0)
        # there's a y inversion don't ask me why

        # _.pixelbuffer = PixelBuffer([_.width,_.height,3],data=b'\x00'*3*_.width*_.height)



    def __texUpdate(_, frame):
        """ Update the texture with the newly supplied frame. """
        # Retrieve buffer from videosink
        if _.texture_locked:
            return
        #with _.pixelbuffer :
        #    _.pixelbuffer.read(frame)
        _.buffer = frame
        _.texUpdated = True

    def update(_):
        if _.texUpdated:
            _.texture_locked = True

            glBindTexture(GL_TEXTURE_2D, _.id)
            glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, _.vidsize[0],
                            _.vidsize[1], GL_RGB,
                            GL_UNSIGNED_BYTE,
                            #GL_UNSIGNED_INT_8_8_8_8_REV,
                            _.buffer)

            '''
            with _.pixelbuffer:

                glPixelStorei(GL_UNPACK_ROW_LENGTH, _.pixelbuffer.width)
                glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
                #glBindTexture(GL_TEXTURE_2D, _.id)

                #glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, m_width, m_height, GL_BGRA, GL_UNSIGNED_INT_8_8_8_8_REV
                #glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, _.vidsize[0],
                #                _.vidsize[1], GL_RGB, GL_UNSIGNED_BYTE,
                #                #None)
                #                _.buffer)

                glBindBuffer(GL_PIXEL_UNPACK_BUFFER, pbos[write_dx])
                glBufferData(GL_PIXEL_UNPACK_BUFFER, num_bytes, NULL, GL_STREAM_DRAW)

                #ptr = glMapBuffer(GL_PIXEL_UNPACK_BUFFER, GL_WRITE_ONLY)

                #if ptr:
                    #memcpy(ptr, pixels, num_bytes)
                glBufferSubData(GL_PIXEL_PACK_BUFFER, 0, _.size, data)

                    #glUnmapBuffer(GL_PIXEL_UNPACK_BUFFER)

                glBindBuffer(GL_PIXEL_UNPACK_BUFFER, 0);
            '''
            _.texture_locked = False
            _.texUpdated = False


    def bind(_):
        glBindTexture(GL_TEXTURE_2D,  _.id)

    def play(_):
        # Start listening for incoming audio frames
        if _.decoder.audioformat:
            _.audio.start()
        _.decoder.play()
        _.paused = False

    def stop(_):
        """ Stops playback. """
        _.decoder.stop()
        logger.info('decoder stopped')

    def pause(_):
        """ Pauses playback. """
        if _.decoder.status == mediadecoder.PAUSED:
            _.decoder.pause()
            _.paused = False
        elif _.decoder.status == mediadecoder.PLAYING:
            _.decoder.pause()
            _.paused = True
        else:
            print("Player not in pausable state")

