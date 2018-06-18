#!/usr/bin/env python

# $URL: http://pypng.googlecode.com/svn/trunk/code/png.py $
# $Rev: 228 $

# png.py - PNG encoder/decoder in pure Python
#
# Modified for Pygame in Oct., 2012 to work with Python 3.x.
#
# Copyright (C) 2006 Johann C. Rocholl <johann@browsershots.org>
# Portions Copyright (C) 2009 David Jones <drj@pobox.com>
# And probably portions Copyright (C) 2006 Nicko van Someren <nicko@nicko.org>
#
# Original concept by Johann C. Rocholl.
#
# LICENSE (The MIT License)
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Changelog (recent first):
# 2009-03-11 David: interlaced bit depth < 8 (writing).
# 2009-03-10 David: interlaced bit depth < 8 (reading).
# 2009-03-04 David: Flat and Boxed pixel formats.
# 2009-02-26 David: Palette support (writing).
# 2009-02-23 David: Bit-depths < 8; better PNM support.
# 2006-06-17 Nicko: Reworked into a class, faster interlacing.
# 2006-06-17 Johann: Very simple prototype PNG decoder.
# 2006-06-17 Nicko: Test suite with various image generators.
# 2006-06-17 Nicko: Alpha-channel, grey-scale, 16-bit/plane support.
# 2006-06-15 Johann: Scanline iterator interface for large input files.
# 2006-06-09 Johann: Very simple prototype PNG encoder.

# Incorporated into Bangai-O Development Tools by drj on 2009-02-11 from
# http://trac.browsershots.org/browser/trunk/pypng/lib/png.py?rev=2885

# Incorporated into pypng by drj on 2009-03-12 from
# //depot/prj/bangaio/master/code/png.py#67


"""
Pure Python PNG Reader/Writer

This Python module implements support for PNG images (see PNG
specification at http://www.w3.org/TR/2003/REC-PNG-20031110/ ). It reads
and writes PNG files with all allowable bit depths (1/2/4/8/16/24/32/48/64
bits per pixel) and colour combinations: greyscale (1/2/4/8/16 bit); RGB,
RGBA, LA (greyscale with alpha) with 8/16 bits per channel; colour mapped
images (1/2/4/8 bit).  Adam7 interlacing is supported for reading and
writing.  A number of optional chunks can be specified (when writing)
and understood (when reading): ``tRNS``, ``bKGD``, ``gAMA``.

For help, type ``import png; help(png)`` in your python interpreter.

A good place to start is the :class:`Reader` and :class:`Writer` classes.

Requires Python 2.3.  Limited support is available for Python 2.2, but
not everything works.  Best with Python 2.4 and higher.  Installation is
trivial, but see the ``README.txt`` file (with the source distribution)
for details.

This file can also be used as a command-line utility to convert
`Netpbm <http://netpbm.sourceforge.net/>`_ PNM files to PNG, and the reverse conversion from PNG to
PNM. The interface is similar to that of the ``pnmtopng`` program from
Netpbm.  Type ``python png.py --help`` at the shell prompt
for usage and a list of options.

A note on spelling and terminology
----------------------------------

Generally British English spelling is used in the documentation.  So
that's "greyscale" and "colour".  This not only matches the author's
native language, it's also used by the PNG specification.

The major colour models supported by PNG (and hence by PyPNG) are:
greyscale, RGB, greyscale--alpha, RGB--alpha.  These are sometimes
referred to using the abbreviations: L, RGB, LA, RGBA.  In this case
each letter abbreviates a single channel: *L* is for Luminance or Luma or
Lightness which is the channel used in greyscale images; *R*, *G*, *B* stand
for Red, Green, Blue, the components of a colour image; *A* stands for
Alpha, the opacity channel (used for transparency effects, but higher
values are more opaque, so it makes sense to call it opacity).

A note on formats
-----------------

When getting pixel data out of this module (reading) and presenting
data to this module (writing) there are a number of ways the data could
be represented as a Python value.  Generally this module uses one of
three formats called "flat row flat pixel", "boxed row flat pixel", and
"boxed row boxed pixel".  Basically the concern is whether each pixel
and each row comes in its own little tuple (box), or not.

Consider an image that is 3 pixels wide by 2 pixels high, and each pixel
has RGB components:

Boxed row flat pixel::

  list([R,G,B, R,G,B, R,G,B],
       [R,G,B, R,G,B, R,G,B])

Each row appears as its own list, but the pixels are flattened so that
three values for one pixel simply follow the three values for the previous
pixel.  This is the most common format used, because it provides a good
compromise between space and convenience.  PyPNG regards itself as
at liberty to replace any sequence type with any sufficiently compatible
other sequence type; in practice each row is an array (from the array
module), and the outer list is sometimes an iterator rather than an
explicit list (so that streaming is possible).

Flat row flat pixel::

  [R,G,B, R,G,B, R,G,B,
   R,G,B, R,G,B, R,G,B]

The entire image is one single giant sequence of colour values.
Generally an array will be used (to save space), not a list.

Boxed row boxed pixel::

  list([ (R,G,B), (R,G,B), (R,G,B) ],
       [ (R,G,B), (R,G,B), (R,G,B) ])

Each row appears in its own list, but each pixel also appears in its own
tuple.  A serious memory burn in Python.

In all cases the top row comes first, and for each row the pixels are
ordered from left-to-right.  Within a pixel the values appear in the
order, R-G-B-A (or L-A for greyscale--alpha).

There is a fourth format, mentioned because it is used internally,
is close to what lies inside a PNG file itself, and has some support
from the public API.  This format is called packed.  When packed,
each row is a sequence of bytes (integers from 0 to 255), just as
it is before PNG scanline filtering is applied.  When the bit depth
is 8 this is essentially the same as boxed row flat pixel; when the
bit depth is less than 8, several pixels are packed into each byte;
when the bit depth is 16 (the only value more than 8 that is supported
by the PNG image format) each pixel value is decomposed into 2 bytes
(and `packed` is a misnomer).  This format is used by the
:meth:`Writer.write_packed` method.  It isn't usually a convenient
format, but may be just right if the source data for the PNG image
comes from something that uses a similar format (for example, 1-bit
BMPs, or another PNG file).

And now, my famous members
--------------------------
"""

# http://www.python.org/doc/2.2.3/whatsnew/node5.html
from __future__ import generators

__version__ = "$URL: http://pypng.googlecode.com/svn/trunk/code/png.py $ $Rev: 228 $"

from pygame.compat import geterror, next_, imap_
from array import array
try: # See :pyver:old
    import itertools
except:
    pass
import math
# http://www.python.org/doc/2.4.4/lib/module-operator.html
import operator
import struct
import sys
import zlib
# http://www.python.org/doc/2.4.4/lib/module-warnings.html
import warnings


__all__ = ['Image', 'Reader', 'Writer', 'write_chunks', 'from_array']


# The PNG signature.
# http://www.w3.org/TR/PNG/#5PNG-file-signature
_signature = struct.pack('8B', 137, 80, 78, 71, 13, 10, 26, 10)

_adam7 = ((0, 0, 8, 8),
          (4, 0, 8, 8),
          (0, 4, 4, 8),
          (2, 0, 4, 4),
          (0, 2, 2, 4),
          (1, 0, 2, 2),
          (0, 1, 1, 2))

def group(s, n):
    # See
    # http://www.python.org/doc/2.6/library/functions.html#zip
    return zip(*[iter(s)]*n)

def isarray(x):
    """Same as ``isinstance(x, array)`` except on Python 2.2, where it
    always returns ``False``.  This helps PyPNG work on Python 2.2.
    """

    try:
        return isinstance(x, array)
    except:
        return False

try:  # see :pyver:old
    array.tostring
except:
    def tostring(row):
        l = len(row)
        return struct.pack('%dB' % l, *row)
else:
    def tostring(row):
        """Convert row of bytes to string.  Expects `row` to be an
        ``array``.
        """
        return row.tostring()

# Conditionally convert to bytes.  Works on Python 2 and Python 3.
try:
    bytes('', 'ascii')
    def strtobytes(x): return bytes(x, 'iso8859-1')
    def bytestostr(x): return str(x, 'iso8859-1')
except:
    strtobytes = str
    bytestostr = str

def interleave_planes(ipixels, apixels, ipsize, apsize):
    """
    Interleave (colour) planes, e.g. RGB + A = RGBA.

    Return an array of pixels consisting of the `ipsize` elements of data
    from each pixel in `ipixels` followed by the `apsize` elements of data
    from each pixel in `apixels`.  Conventionally `ipixels` and
    `apixels` are byte arrays so the sizes are bytes, but it actually
    works with any arrays of the same type.  The returned array is the
    same type as the input arrays which should be the same type as each other.
    """

    itotal = len(ipixels)
    atotal = len(apixels)
    newtotal = itotal + atotal
    newpsize = ipsize + apsize
    # Set up the output buffer
    # See http://www.python.org/doc/2.4.4/lib/module-array.html#l2h-1356
    out = array(ipixels.typecode)
    # It's annoying that there is no cheap way to set the array size :-(
    out.extend(ipixels)
    out.extend(apixels)
    # Interleave in the pixel data
    for i in range(ipsize):
        out[i:newtotal:newpsize] = ipixels[i:itotal:ipsize]
    for i in range(apsize):
        out[i+ipsize:newtotal:newpsize] = apixels[i:atotal:apsize]
    return out

def check_palette(palette):
    """Check a palette argument (to the :class:`Writer` class) for validity.
    Returns the palette as a list if okay; raises an exception otherwise.
    """

    # None is the default and is allowed.
    if palette is None:
        return None

    p = list(palette)
    if not (0 < len(p) <= 256):
        raise ValueError("a palette must have between 1 and 256 entries")
    seen_triple = False
    for i,t in enumerate(p):
        if len(t) not in (3,4):
            raise ValueError(
              "palette entry %d: entries must be 3- or 4-tuples." % i)
        if len(t) == 3:
            seen_triple = True
        if seen_triple and len(t) == 4:
            raise ValueError(
              "palette entry %d: all 4-tuples must precede all 3-tuples" % i)
        for x in t:
            if int(x) != x or not(0 <= x <= 255):
                raise ValueError(
                  "palette entry %d: values must be integer: 0 <= x <= 255" % i)
    return p

class Error(Exception):
    prefix = 'Error'
    def __str__(self):
        return self.prefix + ': ' + ' '.join(self.args)

class FormatError(Error):
    """Problem with input file format.  In other words, PNG file does
    not conform to the specification in some way and is invalid.
    """

    prefix = 'FormatError'

class ChunkError(FormatError):
    prefix = 'ChunkError'


class Writer:
    """
    PNG encoder in pure Python.
    """

    def __init__(self, width=None, height=None,
                 size=None,
                 greyscale=False,
                 alpha=False,
                 bitdepth=8,
                 palette=None,
                 transparent=None,
                 background=None,
                 gamma=None,
                 compression=None,
                 interlace=False,
                 bytes_per_sample=None, # deprecated
                 planes=None,
                 colormap=None,
                 maxval=None,
                 chunk_limit=2**20):
        """
        Create a PNG encoder object.

        Arguments:

        width, height
          Image size in pixels, as two separate arguments.
        size
          Image size (w,h) in pixels, as single argument.
        greyscale
          Input data is greyscale, not RGB.
        alpha
          Input data has alpha channel (RGBA or LA).
        bitdepth
          Bit depth: from 1 to 16.
        palette
          Create a palette for a colour mapped image (colour type 3).
        transparent
          Specify a transparent colour (create a ``tRNS`` chunk).
        background
          Specify a default background colour (create a ``bKGD`` chunk).
        gamma
          Specify a gamma value (create a ``gAMA`` chunk).
        compression
          zlib compression level (1-9).
        interlace
          Create an interlaced image.
        chunk_limit
          Write multiple ``IDAT`` chunks to save memory.

        The image size (in pixels) can be specified either by using the
        `width` and `height` arguments, or with the single `size`
        argument.  If `size` is used it should be a pair (*width*,
        *height*).

        `greyscale` and `alpha` are booleans that specify whether
        an image is greyscale (or colour), and whether it has an
        alpha channel (or not).

        `bitdepth` specifies the bit depth of the source pixel values.
        Each source pixel value must be an integer between 0 and
        ``2**bitdepth-1``.  For example, 8-bit images have values
        between 0 and 255.  PNG only stores images with bit depths of
        1,2,4,8, or 16.  When `bitdepth` is not one of these values,
        the next highest valid bit depth is selected, and an ``sBIT``
        (significant bits) chunk is generated that specifies the original
        precision of the source image.  In this case the supplied pixel
        values will be rescaled to fit the range of the selected bit depth.

        The details of which bit depth / colour model combinations the
        PNG file format supports directly, are somewhat arcane
        (refer to the PNG specification for full details).  Briefly:
        "small" bit depths (1,2,4) are only allowed with greyscale and
        colour mapped images; colour mapped images cannot have bit depth
        16.

        For colour mapped images (in other words, when the `palette`
        argument is specified) the `bitdepth` argument must match one of
        the valid PNG bit depths: 1, 2, 4, or 8.  (It is valid to have a
        PNG image with a palette and an ``sBIT`` chunk, but the meaning
        is slightly different; it would be awkward to press the
        `bitdepth` argument into service for this.)

        The `palette` option, when specified, causes a colour mapped image
        to be created: the PNG colour type is set to 3; greyscale
        must not be set; alpha must not be set; transparent must
        not be set; the bit depth must be 1,2,4, or 8.  When a colour
        mapped image is created, the pixel values are palette indexes
        and the `bitdepth` argument specifies the size of these indexes
        (not the size of the colour values in the palette).

        The palette argument value should be a sequence of 3- or
        4-tuples.  3-tuples specify RGB palette entries; 4-tuples
        specify RGBA palette entries.  If both 4-tuples and 3-tuples
        appear in the sequence then all the 4-tuples must come
        before all the 3-tuples.  A ``PLTE`` chunk is created; if there
        are 4-tuples then a ``tRNS`` chunk is created as well.  The
        ``PLTE`` chunk will contain all the RGB triples in the same
        sequence; the ``tRNS`` chunk will contain the alpha channel for
        all the 4-tuples, in the same sequence.  Palette entries
        are always 8-bit.

        If specified, the `transparent` and `background` parameters must
        be a tuple with three integer values for red, green, blue, or
        a simple integer (or singleton tuple) for a greyscale image.

        If specified, the `gamma` parameter must be a positive number
        (generally, a float).  A ``gAMA`` chunk will be created.  Note that
        this will not change the values of the pixels as they appear in
        the PNG file, they are assumed to have already been converted
        appropriately for the gamma specified.

        The `compression` argument specifies the compression level
        to be used by the ``zlib`` module.  Higher values are likely
        to compress better, but will be slower to compress.  The
        default for this argument is ``None``; this does not mean
        no compression, rather it means that the default from the
        ``zlib`` module is used (which is generally acceptable).

        If `interlace` is true then an interlaced image is created
        (using PNG's so far only interace method, *Adam7*).  This does not
        affect how the pixels should be presented to the encoder, rather
        it changes how they are arranged into the PNG file.  On slow
        connexions interlaced images can be partially decoded by the
        browser to give a rough view of the image that is successively
        refined as more image data appears.

        .. note ::

          Enabling the `interlace` option requires the entire image
          to be processed in working memory.

        `chunk_limit` is used to limit the amount of memory used whilst
        compressing the image.  In order to avoid using large amounts of
        memory, multiple ``IDAT`` chunks may be created.
        """

        # At the moment the `planes` argument is ignored;
        # its purpose is to act as a dummy so that
        # ``Writer(x, y, **info)`` works, where `info` is a dictionary
        # returned by Reader.read and friends.
        # Ditto for `colormap`.

        # A couple of helper functions come first.  Best skipped if you
        # are reading through.

        def isinteger(x):
            try:
                return int(x) == x
            except:
                return False

        def check_color(c, which):
            """Checks that a colour argument for transparent or
            background options is the right form.  Also "corrects" bare
            integers to 1-tuples.
            """

            if c is None:
                return c
            if greyscale:
                try:
                    l = len(c)
                except TypeError:
                    c = (c,)
                if len(c) != 1:
                    raise ValueError("%s for greyscale must be 1-tuple" %
                        which)
                if not isinteger(c[0]):
                    raise ValueError(
                        "%s colour for greyscale must be integer" %
                        which)
            else:
                if not (len(c) == 3 and
                        isinteger(c[0]) and
                        isinteger(c[1]) and
                        isinteger(c[2])):
                    raise ValueError(
                        "%s colour must be a triple of integers" %
                        which)
            return c

        if size:
            if len(size) != 2:
                raise ValueError(
                  "size argument should be a pair (width, height)")
            if width is not None and width != size[0]:
                raise ValueError(
                  "size[0] (%r) and width (%r) should match when both are used."
                    % (size[0], width))
            if height is not None and height != size[1]:
                raise ValueError(
                  "size[1] (%r) and height (%r) should match when both are used."
                    % (size[1], height))
            width,height = size
        del size

        if width <= 0 or height <= 0:
            raise ValueError("width and height must be greater than zero")
        if not isinteger(width) or not isinteger(height):
            raise ValueError("width and height must be integers")
        # http://www.w3.org/TR/PNG/#7Integers-and-byte-order
        if width > 2**32-1 or height > 2**32-1:
            raise ValueError("width and height cannot exceed 2**32-1")

        if alpha and transparent is not None:
            raise ValueError(
                "transparent colour not allowed with alpha channel")

        if bytes_per_sample is not None:
            warnings.warn('please use bitdepth instead of bytes_per_sample',
                          DeprecationWarning)
            if bytes_per_sample not in (0.125, 0.25, 0.5, 1, 2):
                raise ValueError(
                    "bytes per sample must be .125, .25, .5, 1, or 2")
            bitdepth = int(8*bytes_per_sample)
        del bytes_per_sample
        if not isinteger(bitdepth) or bitdepth < 1 or 16 < bitdepth:
            raise ValueError("bitdepth (%r) must be a postive integer <= 16" %
              bitdepth)

        self.rescale = None
        if palette:
            if bitdepth not in (1,2,4,8):
                raise ValueError("with palette, bitdepth must be 1, 2, 4, or 8")
            if transparent is not None:
                raise ValueError("transparent and palette not compatible")
            if alpha:
                raise ValueError("alpha and palette not compatible")
            if greyscale:
                raise ValueError("greyscale and palette not compatible")
        else:
            # No palette, check for sBIT chunk generation.
            if alpha or not greyscale:
                if bitdepth not in (8,16):
                    targetbitdepth = (8,16)[bitdepth > 8]
                    self.rescale = (bitdepth, targetbitdepth)
                    bitdepth = targetbitdepth
                    del targetbitdepth
            else:
                assert greyscale
                assert not alpha
                if bitdepth not in (1,2,4,8,16):
                    if bitdepth > 8:
                        targetbitdepth = 16
                    elif bitdepth == 3:
                        targetbitdepth = 4
                    else:
                        assert bitdepth in (5,6,7)
                        targetbitdepth = 8
                    self.rescale = (bitdepth, targetbitdepth)
                    bitdepth = targetbitdepth
                    del targetbitdepth

        if bitdepth < 8 and (alpha or not greyscale and not palette):
            raise ValueError(
              "bitdepth < 8 only permitted with greyscale or palette")
        if bitdepth > 8 and palette:
            raise ValueError(
                "bit depth must be 8 or less for images with palette")

        transparent = check_color(transparent, 'transparent')
        background = check_color(background, 'background')

        # It's important that the true boolean values (greyscale, alpha,
        # colormap, interlace) are converted to bool because Iverson's
        # convention is relied upon later on.
        self.width = width
        self.height = height
        self.transparent = transparent
        self.background = background
        self.gamma = gamma
        self.greyscale = bool(greyscale)
        self.alpha = bool(alpha)
        self.colormap = bool(palette)
        self.bitdepth = int(bitdepth)
        self.compression = compression
        self.chunk_limit = chunk_limit
        self.interlace = bool(interlace)
        self.palette = check_palette(palette)

        self.color_type = 4*self.alpha + 2*(not greyscale) + 1*self.colormap
        assert self.color_type in (0,2,3,4,6)

        self.color_planes = (3,1)[self.greyscale or self.colormap]
        self.planes = self.color_planes + self.alpha
        # :todo: fix for bitdepth < 8
        self.psize = (self.bitdepth/8) * self.planes

    def make_palette(self):
        """Create the byte sequences for a ``PLTE`` and if necessary a
        ``tRNS`` chunk.  Returned as a pair (*p*, *t*).  *t* will be
        ``None`` if no ``tRNS`` chunk is necessary.
        """

        p = array('B')
        t = array('B')

        for x in self.palette:
            p.extend(x[0:3])
            if len(x) > 3:
                t.append(x[3])
        p = tostring(p)
        t = tostring(t)
        if t:
            return p,t
        return p,None

    def write(self, outfile, rows):
        """Write a PNG image to the output file.  `rows` should be
        an iterable that yields each row in boxed row flat pixel format.
        The rows should be the rows of the original image, so there
        should be ``self.height`` rows of ``self.width * self.planes`` values.
        If `interlace` is specified (when creating the instance), then
        an interlaced PNG file will be written.  Supply the rows in the
        normal image order; the interlacing is carried out internally.

        .. note ::

          Interlacing will require the entire image to be in working memory.
        """

        if self.interlace:
            fmt = 'BH'[self.bitdepth > 8]
            a = array(fmt, itertools.chain(*rows))
            return self.write_array(outfile, a)
        else:
            nrows = self.write_passes(outfile, rows)
            if nrows != self.height:
                raise ValueError(
                  "rows supplied (%d) does not match height (%d)" %
                  (nrows, self.height))

    def write_passes(self, outfile, rows, packed=False):
        """
        Write a PNG image to the output file.

        Most users are expected to find the :meth:`write` or
        :meth:`write_array` method more convenient.

        The rows should be given to this method in the order that
        they appear in the output file.  For straightlaced images,
        this is the usual top to bottom ordering, but for interlaced
        images the rows should have already been interlaced before
        passing them to this function.

        `rows` should be an iterable that yields each row.  When
        `packed` is ``False`` the rows should be in boxed row flat pixel
        format; when `packed` is ``True`` each row should be a packed
        sequence of bytes.

        """

        # http://www.w3.org/TR/PNG/#5PNG-file-signature
        outfile.write(_signature)

        # http://www.w3.org/TR/PNG/#11IHDR
        write_chunk(outfile, 'IHDR',
                    struct.pack("!2I5B", self.width, self.height,
                                self.bitdepth, self.color_type,
                                0, 0, self.interlace))

        # See :chunk:order
        # http://www.w3.org/TR/PNG/#11gAMA
        if self.gamma is not None:
            write_chunk(outfile, 'gAMA',
                        struct.pack("!L", int(round(self.gamma*1e5))))

        # See :chunk:order
        # http://www.w3.org/TR/PNG/#11sBIT
        if self.rescale:
            write_chunk(outfile, 'sBIT',
                struct.pack('%dB' % self.planes,
                            *[self.rescale[0]]*self.planes))

        # :chunk:order: Without a palette (PLTE chunk), ordering is
        # relatively relaxed.  With one, gAMA chunk must precede PLTE
        # chunk which must precede tRNS and bKGD.
        # See http://www.w3.org/TR/PNG/#5ChunkOrdering
        if self.palette:
            p,t = self.make_palette()
            write_chunk(outfile, 'PLTE', p)
            if t:
                # tRNS chunk is optional.  Only needed if palette entries
                # have alpha.
                write_chunk(outfile, 'tRNS', t)

        # http://www.w3.org/TR/PNG/#11tRNS
        if self.transparent is not None:
            if self.greyscale:
                write_chunk(outfile, 'tRNS',
                            struct.pack("!1H", *self.transparent))
            else:
                write_chunk(outfile, 'tRNS',
                            struct.pack("!3H", *self.transparent))

        # http://www.w3.org/TR/PNG/#11bKGD
        if self.background is not None:
            if self.greyscale:
                write_chunk(outfile, 'bKGD',
                            struct.pack("!1H", *self.background))
            else:
                write_chunk(outfile, 'bKGD',
                            struct.pack("!3H", *self.background))

        # http://www.w3.org/TR/PNG/#11IDAT
        if self.compression is not None:
            compressor = zlib.compressobj(self.compression)
        else:
            compressor = zlib.compressobj()

        # Choose an extend function based on the bitdepth.  The extend
        # function packs/decomposes the pixel values into bytes and
        # stuffs them onto the data array.
        data = array('B')
        if self.bitdepth == 8 or packed:
            extend = data.extend
        elif self.bitdepth == 16:
            # Decompose into bytes
            def extend(sl):
                fmt = '!%dH' % len(sl)
                data.extend(array('B', struct.pack(fmt, *sl)))
        else:
            # Pack into bytes
            assert self.bitdepth < 8
            # samples per byte
            spb = int(8/self.bitdepth)
            def extend(sl):
                a = array('B', sl)
                # Adding padding bytes so we can group into a whole
                # number of spb-tuples.
                l = float(len(a))
                extra = math.ceil(l / float(spb))*spb - l
                a.extend([0]*int(extra))
                # Pack into bytes
                l = group(a, spb)
                l = map(lambda e: reduce(lambda x,y:
                                           (x << self.bitdepth) + y, e), l)
                data.extend(l)
        if self.rescale:
            oldextend = extend
            factor = \
              float(2**self.rescale[1]-1) / float(2**self.rescale[0]-1)
            def extend(sl):
                oldextend(map(lambda x: int(round(factor*x)), sl))

        # Build the first row, testing mostly to see if we need to
        # changed the extend function to cope with NumPy integer types
        # (they cause our ordinary definition of extend to fail, so we
        # wrap it).  See
        # http://code.google.com/p/pypng/issues/detail?id=44
        enumrows = enumerate(rows)
        del rows

        # First row's filter type.
        data.append(0)
        # :todo: Certain exceptions in the call to ``.next()`` or the
        # following try would indicate no row data supplied.
        # Should catch.
        i,row = next_(enumrows)
        try:
            # If this fails...
            extend(row)
        except:
            # ... try a version that converts the values to int first.
            # Not only does this work for the (slightly broken) NumPy
            # types, there are probably lots of other, unknown, "nearly"
            # int types it works for.
            def wrapmapint(f):
                return lambda sl: f(map(int, sl))
            extend = wrapmapint(extend)
            del wrapmapint
            extend(row)

        for i,row in enumrows:
            # Add "None" filter type.  Currently, it's essential that
            # this filter type be used for every scanline as we do not
            # mark the first row of a reduced pass image; that means we
            # could accidentally compute the wrong filtered scanline if
            # we used "up", "average", or "paeth" on such a line.
            data.append(0)
            extend(row)
            if len(data) > self.chunk_limit:
                compressed = compressor.compress(tostring(data))
                if len(compressed):
                    # print >> sys.stderr, len(data), len(compressed)
                    write_chunk(outfile, 'IDAT', compressed)
                # Because of our very witty definition of ``extend``,
                # above, we must re-use the same ``data`` object.  Hence
                # we use ``del`` to empty this one, rather than create a
                # fresh one (which would be my natural FP instinct).
                del data[:]
        if len(data):
            compressed = compressor.compress(tostring(data))
        else:
            compressed = ''
        flushed = compressor.flush()
        if len(compressed) or len(flushed):
            # print >> sys.stderr, len(data), len(compressed), len(flushed)
            write_chunk(outfile, 'IDAT', compressed + flushed)
        # http://www.w3.org/TR/PNG/#11IEND
        write_chunk(outfile, 'IEND')
        return i+1

    def write_array(self, outfile, pixels):
        """
        Write an array in flat row flat pixel format as a PNG file on
        the output file.  See also :meth:`write` method.
        """

        if self.interlace:
            self.write_passes(outfile, self.array_scanlines_interlace(pixels))
        else:
            self.write_passes(outfile, self.array_scanlines(pixels))

    def write_packed(self, outfile, rows):
        """
        Write PNG file to `outfile`.  The pixel data comes from `rows`
        which should be in boxed row packed format.  Each row should be
        a sequence of packed bytes.

        Technically, this method does work for interlaced images but it
        is best avoided.  For interlaced images, the rows should be
        presented in the order that they appear in the file.

        This method should not be used when the source image bit depth
        is not one naturally supported by PNG; the bit depth should be
        1, 2, 4, 8, or 16.
        """

        if self.rescale:
            raise Error("write_packed method not suitable for bit depth %d" %
              self.rescale[0])
        return self.write_passes(outfile, rows, packed=True)

    def convert_pnm(self, infile, outfile):
        """
        Convert a PNM file containing raw pixel data into a PNG file
        with the parameters set in the writer object.  Works for
        (binary) PGM, PPM, and PAM formats.
        """

        if self.interlace:
            pixels = array('B')
            pixels.fromfile(infile,
                            (self.bitdepth/8) * self.color_planes *
                            self.width * self.height)
            self.write_passes(outfile, self.array_scanlines_interlace(pixels))
        else:
            self.write_passes(outfile, self.file_scanlines(infile))

    def convert_ppm_and_pgm(self, ppmfile, pgmfile, outfile):
        """
        Convert a PPM and PGM file containing raw pixel data into a
        PNG outfile with the parameters set in the writer object.
        """
        pixels = array('B')
        pixels.fromfile(ppmfile,
                        (self.bitdepth/8) * self.color_planes *
                        self.width * self.height)
        apixels = array('B')
        apixels.fromfile(pgmfile,
                         (self.bitdepth/8) *
                         self.width * self.height)
        pixels = interleave_planes(pixels, apixels,
                                   (self.bitdepth/8) * self.color_planes,
                                   (self.bitdepth/8))
        if self.interlace:
            self.write_passes(outfile, self.array_scanlines_interlace(pixels))
        else:
            self.write_passes(outfile, self.array_scanlines(pixels))

    def file_scanlines(self, infile):
        """
        Generates boxed rows in flat pixel format, from the input file
        `infile`.  It assumes that the input file is in a "Netpbm-like"
        binary format, and is positioned at the beginning of the first
        pixel.  The number of pixels to read is taken from the image
        dimensions (`width`, `height`, `planes`) and the number of bytes
        per value is implied by the image `bitdepth`.
        """

        # Values per row
        vpr = self.width * self.planes
        row_bytes = vpr
        if self.bitdepth > 8:
            assert self.bitdepth == 16
            row_bytes *= 2
            fmt = '>%dH' % vpr
            def line():
                return array('H', struct.unpack(fmt, infile.read(row_bytes)))
        else:
            def line():
                scanline = array('B', infile.read(row_bytes))
                return scanline
        for y in range(self.height):
            yield line()

    def array_scanlines(self, pixels):
        """
        Generates boxed rows (flat pixels) from flat rows (flat pixels)
        in an array.
        """

        # Values per row
        vpr = self.width * self.planes
        stop = 0
        for y in range(self.height):
            start = stop
            stop = start + vpr
            yield pixels[start:stop]

    def array_scanlines_interlace(self, pixels):
        """
        Generator for interlaced scanlines from an array.  `pixels` is
        the full source image in flat row flat pixel format.  The
        generator yields each scanline of the reduced passes in turn, in
        boxed row flat pixel format.
        """

        # http://www.w3.org/TR/PNG/#8InterlaceMethods
        # Array type.
        fmt = 'BH'[self.bitdepth > 8]
        # Value per row
        vpr = self.width * self.planes
        for xstart, ystart, xstep, ystep in _adam7:
            if xstart >= self.width:
                continue
            # Pixels per row (of reduced image)
            ppr = int(math.ceil((self.width-xstart)/float(xstep)))
            # number of values in reduced image row.
            row_len = ppr*self.planes
            for y in range(ystart, self.height, ystep):
                if xstep == 1:
                    offset = y * vpr
                    yield pixels[offset:offset+vpr]
                else:
                    row = array(fmt)
                    # There's no easier way to set the length of an array
                    row.extend(pixels[0:row_len])
                    offset = y * vpr + xstart * self.planes
                    end_offset = (y+1) * vpr
                    skip = self.planes * xstep
                    for i in range(self.planes):
                        row[i::self.planes] = \
                            pixels[offset+i:end_offset:skip]
                    yield row

def write_chunk(outfile, tag, data=strtobytes('')):
    """
    Write a PNG chunk to the output file, including length and
    checksum.
    """

    # http://www.w3.org/TR/PNG/#5Chunk-layout
    outfile.write(struct.pack("!I", len(data)))
    tag = strtobytes(tag)
    outfile.write(tag)
    outfile.write(data)
    checksum = zlib.crc32(tag)
    checksum = zlib.crc32(data, checksum)
    checksum &= 2**32-1
    outfile.write(struct.pack("!I", checksum))

def write_chunks(out, chunks):
    """Create a PNG file by writing out the chunks."""

    out.write(_signature)
    for chunk in chunks:
        write_chunk(out, *chunk)

def filter_scanline(type, line, fo, prev=None):
    """Apply a scanline filter to a scanline.  `type` specifies the
    filter type (0 to 4); `line` specifies the current (unfiltered)
    scanline as a sequence of bytes; `prev` specifies the previous
    (unfiltered) scanline as a sequence of bytes. `fo` specifies the
    filter offset; normally this is size of a pixel in bytes (the number
    of bytes per sample times the number of channels), but when this is
    < 1 (for bit depths < 8) then the filter offset is 1.
    """

    assert 0 <= type < 5

    # The output array.  Which, pathetically, we extend one-byte at a
    # time (fortunately this is linear).
    out = array('B', [type])

    def sub():
        ai = -fo
        for x in line:
            if ai >= 0:
                x = (x - line[ai]) & 0xff
            out.append(x)
            ai += 1
    def up():
        for i,x in enumerate(line):
            x = (x - prev[i]) & 0xff
            out.append(x)
    def average():
        ai = -fo
        for i,x in enumerate(line):
            if ai >= 0:
                x = (x - ((line[ai] + prev[i]) >> 1)) & 0xff
            else:
                x = (x - (prev[i] >> 1)) & 0xff
            out.append(x)
            ai += 1
    def paeth():
        # http://www.w3.org/TR/PNG/#9Filter-type-4-Paeth
        ai = -fo # also used for ci
        for i,x in enumerate(line):
            a = 0
            b = prev[i]
            c = 0

            if ai >= 0:
                a = line[ai]
                c = prev[ai]
            p = a + b - c
            pa = abs(p - a)
            pb = abs(p - b)
            pc = abs(p - c)
            if pa <= pb and pa <= pc: Pr = a
            elif pb <= pc: Pr = b
            else: Pr = c

            x = (x - Pr) & 0xff
            out.append(x)
            ai += 1

    if not prev:
        # We're on the first line.  Some of the filters can be reduced
        # to simpler cases which makes handling the line "off the top"
        # of the image simpler.  "up" becomes "none"; "paeth" becomes
        # "left" (non-trivial, but true). "average" needs to be handled
        # specially.
        if type == 2: # "up"
            return line # type = 0
        elif type == 3:
            prev = [0]*len(line)
        elif type == 4: # "paeth"
            type = 1
    if type == 0:
        out.extend(line)
    elif type == 1:
        sub()
    elif type == 2:
        up()
    elif type == 3:
        average()
    else: # type == 4
        paeth()
    return out


def from_array(a, mode=None, info={}):
    """Create a PNG :class:`Image` object from a 2- or 3-dimensional array.
    One application of this function is easy PIL-style saving:
    ``png.from_array(pixels, 'L').save('foo.png')``.

    .. note :

      The use of the term *3-dimensional* is for marketing purposes
      only.  It doesn't actually work.  Please bear with us.  Meanwhile
      enjoy the complimentary snacks (on request) and please use a
      2-dimensional array.

    Unless they are specified using the *info* parameter, the PNG's
    height and width are taken from the array size.  For a 3 dimensional
    array the first axis is the height; the second axis is the width;
    and the third axis is the channel number.  Thus an RGB image that is
    16 pixels high and 8 wide will use an array that is 16x8x3.  For 2
    dimensional arrays the first axis is the height, but the second axis
    is ``width*channels``, so an RGB image that is 16 pixels high and 8
    wide will use a 2-dimensional array that is 16x24 (each row will be
    8*3==24 sample values).

    *mode* is a string that specifies the image colour format in a
    PIL-style mode.  It can be:

    ``'L'``
      greyscale (1 channel)
    ``'LA'``
      greyscale with alpha (2 channel)
    ``'RGB'``
      colour image (3 channel)
    ``'RGBA'``
      colour image with alpha (4 channel)

    The mode string can also specify the bit depth (overriding how this
    function normally derives the bit depth, see below).  Appending
    ``';16'`` to the mode will cause the PNG to be 16 bits per channel;
    any decimal from 1 to 16 can be used to specify the bit depth.

    When a 2-dimensional array is used *mode* determines how many
    channels the image has, and so allows the width to be derived from
    the second array dimension.

    The array is expected to be a ``numpy`` array, but it can be any
    suitable Python sequence.  For example, a list of lists can be used:
    ``png.from_array([[0, 255, 0], [255, 0, 255]], 'L')``.  The exact
    rules are: ``len(a)`` gives the first dimension, height;
    ``len(a[0])`` gives the second dimension; ``len(a[0][0])`` gives the
    third dimension, unless an exception is raised in which case a
    2-dimensional array is assumed.  It's slightly more complicated than
    that because an iterator of rows can be used, and it all still
    works.  Using an iterator allows data to be streamed efficiently.

    The bit depth of the PNG is normally taken from the array element's
    datatype (but if *mode* specifies a bitdepth then that is used
    instead).  The array element's datatype is determined in a way which
    is supposed to work both for ``numpy`` arrays and for Python
    ``array.array`` objects.  A 1 byte datatype will give a bit depth of
    8, a 2 byte datatype will give a bit depth of 16.  If the datatype
    does not have an implicit size, for example it is a plain Python
    list of lists, as above, then a default of 8 is used.

    The *info* parameter is a dictionary that can be used to specify
    metadata (in the same style as the arguments to the
    :class:``png.Writer`` class).  For this function the keys that are
    useful are:

    height
      overrides the height derived from the array dimensions and allows
      *a* to be an iterable.
    width
      overrides the width derived from the array dimensions.
    bitdepth
      overrides the bit depth derived from the element datatype (but
      must match *mode* if that also specifies a bit depth).

    Generally anything specified in the
    *info* dictionary will override any implicit choices that this
    function would otherwise make, but must match any explicit ones.
    For example, if the *info* dictionary has a ``greyscale`` key then
    this must be true when mode is ``'L'`` or ``'LA'`` and false when
    mode is ``'RGB'`` or ``'RGBA'``.
    """

    # We abuse the *info* parameter by modifying it.  Take a copy here.
    # (Also typechecks *info* to some extent).
    info = dict(info)

    # Syntax check mode string.
    bitdepth = None
    try:
        mode = mode.split(';')
        if len(mode) not in (1,2):
            raise Error()
        if mode[0] not in ('L', 'LA', 'RGB', 'RGBA'):
            raise Error()
        if len(mode) == 2:
            try:
                bitdepth = int(mode[1])
            except:
                raise Error()
    except Error:
        raise Error("mode string should be 'RGB' or 'L;16' or similar.")
    mode = mode[0]

    # Get bitdepth from *mode* if possible.
    if bitdepth:
        if info.get('bitdepth') and bitdepth != info['bitdepth']:
            raise Error("mode bitdepth (%d) should match info bitdepth (%d)." %
              (bitdepth, info['bitdepth']))
        info['bitdepth'] = bitdepth

    # Fill in and/or check entries in *info*.
    # Dimensions.
    if 'size' in info:
        # Check width, height, size all match where used.
        for dimension,axis in [('width', 0), ('height', 1)]:
            if dimension in info:
                if info[dimension] != info['size'][axis]:
                    raise Error(
                      "info[%r] shhould match info['size'][%r]." %
                      (dimension, axis))
        info['width'],info['height'] = info['size']
    if 'height' not in info:
        try:
            l = len(a)
        except:
            raise Error(
              "len(a) does not work, supply info['height'] instead.")
        info['height'] = l
    # Colour format.
    if 'greyscale' in info:
        if bool(info['greyscale']) != ('L' in mode):
            raise Error("info['greyscale'] should match mode.")
    info['greyscale'] = 'L' in mode
    if 'alpha' in info:
        if bool(info['alpha']) != ('A' in mode):
            raise Error("info['alpha'] should match mode.")
    info['alpha'] = 'A' in mode

    planes = len(mode)
    if 'planes' in info:
        if info['planes'] != planes:
            raise Error("info['planes'] should match mode.")

    # In order to work out whether we the array is 2D or 3D we need its
    # first row, which requires that we take a copy of its iterator.
    # We may also need the first row to derive width and bitdepth.
    a,t = itertools.tee(a)
    row = next_(t)
    del t
    try:
        row[0][0]
        threed = True
        testelement = row[0]
    except:
        threed = False
        testelement = row
    if 'width' not in info:
        if threed:
            width = len(row)
        else:
            width = len(row) // planes
        info['width'] = width

    # Not implemented yet
    assert not threed

    if 'bitdepth' not in info:
        try:
            dtype = testelement.dtype
            # goto the "else:" clause.  Sorry.
        except:
            try:
                # Try a Python array.array.
                bitdepth = 8 * testelement.itemsize
            except:
                # We can't determine it from the array element's
                # datatype, use a default of 8.
                bitdepth = 8
        else:
            # If we got here without exception, we now assume that
            # the array is a numpy array.
            if dtype.kind == 'b':
                bitdepth = 1
            else:
                bitdepth = 8 * dtype.itemsize
        info['bitdepth'] = bitdepth

    for thing in 'width height bitdepth greyscale alpha'.split():
        assert thing in info
    return Image(a, info)

# So that refugee's from PIL feel more at home.  Not documented.
fromarray = from_array

class Image:
    """A PNG image.
    You can create an :class:`Image` object from an array of pixels by calling
    :meth:`png.from_array`.  It can be saved to disk with the
    :meth:`save` method."""
    def __init__(self, rows, info):
        """
        .. note ::

          The constructor is not public.  Please do not call it.
        """

        self.rows = rows
        self.info = info

    def save(self, file):
        """Save the image to *file*.  If *file* looks like an open file
        descriptor then it is used, otherwise it is treated as a
        filename and a fresh file is opened.

        In general, you can only call this method once; after it has
        been called the first time and the PNG image has been saved, the
        source data will have been streamed, and cannot be streamed
        again.
        """

        w = Writer(**self.info)

        try:
            file.write
            def close(): pass
        except:
            file = open(file, 'wb')
            def close(): file.close()

        try:
            w.write(file, self.rows)
        finally:
            close()

class _readable:
    """
    A simple file-like interface for strings and arrays.
    """

    def __init__(self, buf):
        self.buf = buf
        self.offset = 0

    def read(self, n):
        r = self.buf[self.offset:self.offset+n]
        if isarray(r):
            r = r.tostring()
        self.offset += n
        return r


class Reader:
    """
    PNG decoder in pure Python.
    """

    def __init__(self, _guess=None, **kw):
        """
        Create a PNG decoder object.

        The constructor expects exactly one keyword argument. If you
        supply a positional argument instead, it will guess the input
        type. You can choose among the following keyword arguments:

        filename
          Name of input file (a PNG file).
        file
          A file-like object (object with a read() method).
        bytes
          ``array`` or ``string`` with PNG data.

        """
        if ((_guess is not None and len(kw) != 0) or
            (_guess is None and len(kw) != 1)):
            raise TypeError("Reader() takes exactly 1 argument")

        # Will be the first 8 bytes, later on.  See validate_signature.
        self.signature = None
        self.transparent = None
        # A pair of (len,type) if a chunk has been read but its data and
        # checksum have not (in other words the file position is just
        # past the 4 bytes that specify the chunk type).  See preamble
        # method for how this is used.
        self.atchunk = None

        if _guess is not None:
            if isarray(_guess):
                kw["bytes"] = _guess
            elif isinstance(_guess, str):
                kw["filename"] = _guess
            elif isinstance(_guess, file):
                kw["file"] = _guess

        if "filename" in kw:
            self.file = open(kw["filename"], "rb")
        elif "file" in kw:
            self.file = kw["file"]
        elif "bytes" in kw:
            self.file = _readable(kw["bytes"])
        else:
            raise TypeError("expecting filename, file or bytes array")

    def chunk(self, seek=None):
        """
        Read the next PNG chunk from the input file; returns a
        (*type*,*data*) tuple.  *type* is the chunk's type as a string
        (all PNG chunk types are 4 characters long).  *data* is the
        chunk's data content, as a string.

        If the optional `seek` argument is
        specified then it will keep reading chunks until it either runs
        out of file or finds the type specified by the argument.  Note
        that in general the order of chunks in PNGs is unspecified, so
        using `seek` can cause you to miss chunks.
        """

        self.validate_signature()

        while True:
            # http://www.w3.org/TR/PNG/#5Chunk-layout
            if not self.atchunk:
                self.atchunk = self.chunklentype()
            length,type = self.atchunk
            self.atchunk = None
            data = self.file.read(length)
            if len(data) != length:
                raise ChunkError('Chunk %s too short for required %i octets.'
                  % (type, length))
            checksum = self.file.read(4)
            if len(checksum) != 4:
                raise ValueError('Chunk %s too short for checksum.', tag)
            if seek and type != seek:
                continue
            verify = zlib.crc32(strtobytes(type))
            verify = zlib.crc32(data, verify)
            # Whether the output from zlib.crc32 is signed or not varies
            # according to hideous implementation details, see
            # http://bugs.python.org/issue1202 .
            # We coerce it to be positive here (in a way which works on
            # Python 2.3 and older).
            verify &= 2**32 - 1
            verify = struct.pack('!I', verify)
            if checksum != verify:
                # print repr(checksum)
                (a, ) = struct.unpack('!I', checksum)
                (b, ) = struct.unpack('!I', verify)
                raise ChunkError(
                  "Checksum error in %s chunk: 0x%08X != 0x%08X." %
                  (type, a, b))
            return type, data

    def chunks(self):
        """Return an iterator that will yield each chunk as a
        (*chunktype*, *content*) pair.
        """

        while True:
            t,v = self.chunk()
            yield t,v
            if t == 'IEND':
                break

    def undo_filter(self, filter_type, scanline, previous):
        """Undo the filter for a scanline.  `scanline` is a sequence of
        bytes that does not include the initial filter type byte.
        `previous` is decoded previous scanline (for straightlaced
        images this is the previous pixel row, but for interlaced
        images, it is the previous scanline in the reduced image, which
        in general is not the previous pixel row in the final image).
        When there is no previous scanline (the first row of a
        straightlaced image, or the first row in one of the passes in an
        interlaced image), then this argument should be ``None``.

        The scanline will have the effects of filtering removed, and the
        result will be returned as a fresh sequence of bytes.
        """

        # :todo: Would it be better to update scanline in place?

        # Create the result byte array.  It seems that the best way to
        # create the array to be the right size is to copy from an
        # existing sequence.  *sigh*
        # If we fill the result with scanline, then this allows a
        # micro-optimisation in the "null" and "sub" cases.
        result = array('B', scanline)

        if filter_type == 0:
            # And here, we _rely_ on filling the result with scanline,
            # above.
            return result

        if filter_type not in (1,2,3,4):
            raise FormatError('Invalid PNG Filter Type.'
              '  See http://www.w3.org/TR/2003/REC-PNG-20031110/#9Filters .')

        # Filter unit.  The stride from one pixel to the corresponding
        # byte from the previous previous.  Normally this is the pixel
        # size in bytes, but when this is smaller than 1, the previous
        # byte is used instead.
        fu = max(1, self.psize)

        # For the first line of a pass, synthesize a dummy previous
        # line.  An alternative approach would be to observe that on the
        # first line 'up' is the same as 'null', 'paeth' is the same
        # as 'sub', with only 'average' requiring any special case.
        if not previous:
            previous = array('B', [0]*len(scanline))

        def sub():
            """Undo sub filter."""

            ai = 0
            # Loops starts at index fu.  Observe that the initial part
            # of the result is already filled in correctly with
            # scanline.
            for i in range(fu, len(result)):
                x = scanline[i]
                a = result[ai]
                result[i] = (x + a) & 0xff
                ai += 1

        def up():
            """Undo up filter."""

            for i in range(len(result)):
                x = scanline[i]
                b = previous[i]
                result[i] = (x + b) & 0xff

        def average():
            """Undo average filter."""

            ai = -fu
            for i in range(len(result)):
                x = scanline[i]
                if ai < 0:
                    a = 0
                else:
                    a = result[ai]
                b = previous[i]
                result[i] = (x + ((a + b) >> 1)) & 0xff
                ai += 1

        def paeth():
            """Undo Paeth filter."""

            # Also used for ci.
            ai = -fu
            for i in range(len(result)):
                x = scanline[i]
                if ai < 0:
                    a = c = 0
                else:
                    a = result[ai]
                    c = previous[ai]
                b = previous[i]
                p = a + b - c
                pa = abs(p - a)
                pb = abs(p - b)
                pc = abs(p - c)
                if pa <= pb and pa <= pc:
                    pr = a
                elif pb <= pc:
                    pr = b
                else:
                    pr = c
                result[i] = (x + pr) & 0xff
                ai += 1

        # Call appropriate filter algorithm.  Note that 0 has already
        # been dealt with.
        (None, sub, up, average, paeth)[filter_type]()
        return result

    def deinterlace(self, raw):
        """
        Read raw pixel data, undo filters, deinterlace, and flatten.
        Return in flat row flat pixel format.
        """

        # print >> sys.stderr, ("Reading interlaced, w=%s, r=%s, planes=%s," +
        #     " bpp=%s") % (self.width, self.height, self.planes, self.bps)
        # Values per row (of the target image)
        vpr = self.width * self.planes

        # Make a result array, and make it big enough.  Interleaving
        # writes to the output array randomly (well, not quite), so the
        # entire output array must be in memory.
        fmt = 'BH'[self.bitdepth > 8]
        a = array(fmt, [0]*vpr*self.height)
        source_offset = 0

        for xstart, ystart, xstep, ystep in _adam7:
            # print >> sys.stderr, "Adam7: start=%s,%s step=%s,%s" % (
            #     xstart, ystart, xstep, ystep)
            if xstart >= self.width:
                continue
            # The previous (reconstructed) scanline.  None at the
            # beginning of a pass to indicate that there is no previous
            # line.
            recon = None
            # Pixels per row (reduced pass image)
            ppr = int(math.ceil((self.width-xstart)/float(xstep)))
            # Row size in bytes for this pass.
            row_size = int(math.ceil(self.psize * ppr))
            for y in range(ystart, self.height, ystep):
                filter_type = raw[source_offset]
                source_offset += 1
                scanline = raw[source_offset:source_offset+row_size]
                source_offset += row_size
                recon = self.undo_filter(filter_type, scanline, recon)
                # Convert so that there is one element per pixel value
                flat = self.serialtoflat(recon, ppr)
                if xstep == 1:
                    assert xstart == 0
                    offset = y * vpr
                    a[offset:offset+vpr] = flat
                else:
                    offset = y * vpr + xstart * self.planes
                    end_offset = (y+1) * vpr
                    skip = self.planes * xstep
                    for i in range(self.planes):
                        a[offset+i:end_offset:skip] = \
                            flat[i::self.planes]
        return a

    def iterboxed(self, rows):
        """Iterator that yields each scanline in boxed row flat pixel
        format.  `rows` should be an iterator that yields the bytes of
        each row in turn.
        """

        def asvalues(raw):
            """Convert a row of raw bytes into a flat row.  Result may
            or may not share with argument"""

            if self.bitdepth == 8:
                return raw
            if self.bitdepth == 16:
                raw = tostring(raw)
                return array('H', struct.unpack('!%dH' % (len(raw)//2), raw))
            assert self.bitdepth < 8
            width = self.width
            # Samples per byte
            spb = 8//self.bitdepth
            out = array('B')
            mask = 2**self.bitdepth - 1
            shifts = map(self.bitdepth.__mul__, reversed(range(spb)))
            for o in raw:
                out.extend(map(lambda i: mask&(o>>i), shifts))
            return out[:width]

        return imap_(asvalues, rows)

    def serialtoflat(self, bytes, width=None):
        """Convert serial format (byte stream) pixel data to flat row
        flat pixel.
        """

        if self.bitdepth == 8:
            return bytes
        if self.bitdepth == 16:
            bytes = tostring(bytes)
            return array('H',
              struct.unpack('!%dH' % (len(bytes)//2), bytes))
        assert self.bitdepth < 8
        if width is None:
            width = self.width
        # Samples per byte
        spb = 8//self.bitdepth
        out = array('B')
        mask = 2**self.bitdepth - 1
        shifts = map(self.bitdepth.__mul__, reversed(range(spb)))
        l = width
        for o in bytes:
            out.extend([(mask&(o>>s)) for s in shifts][:l])
            l -= spb
            if l <= 0:
                l = width
        return out

    def iterstraight(self, raw):
        """Iterator that undoes the effect of filtering, and yields each
        row in serialised format (as a sequence of bytes).  Assumes input
        is straightlaced.  `raw` should be an iterable that yields the
        raw bytes in chunks of arbitrary size."""

        # length of row, in bytes
        rb = self.row_bytes
        a = array('B')
        # The previous (reconstructed) scanline.  None indicates first
        # line of image.
        recon = None
        for some in raw:
            a.extend(some)
            while len(a) >= rb + 1:
                filter_type = a[0]
                scanline = a[1:rb+1]
                del a[:rb+1]
                recon = self.undo_filter(filter_type, scanline, recon)
                yield recon
        if len(a) != 0:
            # :file:format We get here with a file format error: when the
            # available bytes (after decompressing) do not pack into exact
            # rows.
            raise FormatError(
              'Wrong size for decompressed IDAT chunk.')
        assert len(a) == 0

    def validate_signature(self):
        """If signature (header) has not been read then read and
        validate it; otherwise do nothing.
        """

        if self.signature:
            return
        self.signature = self.file.read(8)
        if self.signature != _signature:
            raise FormatError("PNG file has invalid signature.")

    def preamble(self):
        """
        Extract the image metadata by reading the initial part of the PNG
        file up to the start of the ``IDAT`` chunk.  All the chunks that
        precede the ``IDAT`` chunk are read and either processed for
        metadata or discarded.
        """

        self.validate_signature()

        while True:
            if not self.atchunk:
                self.atchunk = self.chunklentype()
                if self.atchunk is None:
                    raise FormatError(
                      'This PNG file has no IDAT chunks.')
            if self.atchunk[1] == 'IDAT':
                return
            self.process_chunk()

    def chunklentype(self):
        """Reads just enough of the input to determine the next
        chunk's length and type, returned as a (*length*, *type*) pair
        where *type* is a string.  If there are no more chunks, ``None``
        is returned.
        """

        x = self.file.read(8)
        if not x:
            return None
        if len(x) != 8:
            raise FormatError(
              'End of file whilst reading chunk length and type.')
        length,type = struct.unpack('!I4s', x)
        type = bytestostr(type)
        if length > 2**31-1:
            raise FormatError('Chunk %s is too large: %d.' % (type,length))
        return length,type

    def process_chunk(self):
        """Process the next chunk and its data.  This only processes the
        following chunk types, all others are ignored: ``IHDR``,
        ``PLTE``, ``bKGD``, ``tRNS``, ``gAMA``, ``sBIT``.
        """

        type, data = self.chunk()
        if type == 'IHDR':
            # http://www.w3.org/TR/PNG/#11IHDR
            if len(data) != 13:
                raise FormatError('IHDR chunk has incorrect length.')
            (self.width, self.height, self.bitdepth, self.color_type,
             self.compression, self.filter,
             self.interlace) = struct.unpack("!2I5B", data)

            # Check that the header specifies only valid combinations.
            if self.bitdepth not in (1,2,4,8,16):
                raise Error("invalid bit depth %d" % self.bitdepth)
            if self.color_type not in (0,2,3,4,6):
                raise Error("invalid colour type %d" % self.color_type)
            # Check indexed (palettized) images have 8 or fewer bits
            # per pixel; check only indexed or greyscale images have
            # fewer than 8 bits per pixel.
            if ((self.color_type & 1 and self.bitdepth > 8) or
                (self.bitdepth < 8 and self.color_type not in (0,3))):
                raise FormatError("Illegal combination of bit depth (%d)"
                  " and colour type (%d)."
                  " See http://www.w3.org/TR/2003/REC-PNG-20031110/#table111 ."
                  % (self.bitdepth, self.color_type))
            if self.compression != 0:
                raise Error("unknown compression method %d" % self.compression)
            if self.filter != 0:
                raise FormatError("Unknown filter method %d,"
                  " see http://www.w3.org/TR/2003/REC-PNG-20031110/#9Filters ."
                  % self.filter)
            if self.interlace not in (0,1):
                raise FormatError("Unknown interlace method %d,"
                  " see http://www.w3.org/TR/2003/REC-PNG-20031110/#8InterlaceMethods ."
                  % self.interlace)

            # Derived values
            # http://www.w3.org/TR/PNG/#6Colour-values
            colormap =  bool(self.color_type & 1)
            greyscale = not (self.color_type & 2)
            alpha = bool(self.color_type & 4)
            color_planes = (3,1)[greyscale or colormap]
            planes = color_planes + alpha

            self.colormap = colormap
            self.greyscale = greyscale
            self.alpha = alpha
            self.color_planes = color_planes
            self.planes = planes
            self.psize = float(self.bitdepth)/float(8) * planes
            if int(self.psize) == self.psize:
                self.psize = int(self.psize)
            self.row_bytes = int(math.ceil(self.width * self.psize))
            # Stores PLTE chunk if present, and is used to check
            # chunk ordering constraints.
            self.plte = None
            # Stores tRNS chunk if present, and is used to check chunk
            # ordering constraints.
            self.trns = None
            # Stores sbit chunk if present.
            self.sbit = None
        elif type == 'PLTE':
            # http://www.w3.org/TR/PNG/#11PLTE
            if self.plte:
                warnings.warn("Multiple PLTE chunks present.")
            self.plte = data
            if len(data) % 3 != 0:
                raise FormatError(
                  "PLTE chunk's length should be a multiple of 3.")
            if len(data) > (2**self.bitdepth)*3:
                raise FormatError("PLTE chunk is too long.")
            if len(data) == 0:
                raise FormatError("Empty PLTE is not allowed.")
        elif type == 'bKGD':
            try:
                if self.colormap:
                    if not self.plte:
                        warnings.warn(
                          "PLTE chunk is required before bKGD chunk.")
                    self.background = struct.unpack('B', data)
                else:
                    self.background = struct.unpack("!%dH" % self.color_planes,
                      data)
            except struct.error:
                raise FormatError("bKGD chunk has incorrect length.")
        elif type == 'tRNS':
            # http://www.w3.org/TR/PNG/#11tRNS
            self.trns = data
            if self.colormap:
                if not self.plte:
                    warnings.warn("PLTE chunk is required before tRNS chunk.")
                else:
                    if len(data) > len(self.plte)/3:
                        # Was warning, but promoted to Error as it
                        # would otherwise cause pain later on.
                        raise FormatError("tRNS chunk is too long.")
            else:
                if self.alpha:
                    raise FormatError(
                      "tRNS chunk is not valid with colour type %d." %
                      self.color_type)
                try:
                    self.transparent = \
                        struct.unpack("!%dH" % self.color_planes, data)
                except struct.error:
                    raise FormatError("tRNS chunk has incorrect length.")
        elif type == 'gAMA':
            try:
                self.gamma = struct.unpack("!L", data)[0] / 100000.0
            except struct.error:
                raise FormatError("gAMA chunk has incorrect length.")
        elif type == 'sBIT':
            self.sbit = data
            if (self.colormap and len(data) != 3 or
                not self.colormap and len(data) != self.planes):
                raise FormatError("sBIT chunk has incorrect length.")

    def read(self):
        """
        Read the PNG file and decode it.  Returns (`width`, `height`,
        `pixels`, `metadata`).

        May use excessive memory.

        `pixels` are returned in boxed row flat pixel format.
        """

        def iteridat():
            """Iterator that yields all the ``IDAT`` chunks as strings."""
            while True:
                try:
                    type, data = self.chunk()
                except ValueError:
                    e = geterror()
                    raise ChunkError(e.args[0])
                if type == 'IEND':
                    # http://www.w3.org/TR/PNG/#11IEND
                    break
                if type != 'IDAT':
                    continue
                # type == 'IDAT'
                # http://www.w3.org/TR/PNG/#11IDAT
                if self.colormap and not self.plte:
                    warnings.warn("PLTE chunk is required before IDAT chunk")
                yield data

        def iterdecomp(idat):
            """Iterator that yields decompressed strings.  `idat` should
            be an iterator that yields the ``IDAT`` chunk data.
            """

            # Currently, with no max_length paramter to decompress, this
            # routine will do one yield per IDAT chunk.  So not very
            # incremental.
            d = zlib.decompressobj()
            # Each IDAT chunk is passed to the decompressor, then any
            # remaining state is decompressed out.
            for data in idat:
                # :todo: add a max_length argument here to limit output
                # size.
                yield array('B', d.decompress(data))
            yield array('B', d.flush())

        self.preamble()
        raw = iterdecomp(iteridat())

        if self.interlace:
            raw = array('B', itertools.chain(*raw))
            arraycode = 'BH'[self.bitdepth>8]
            # Like :meth:`group` but producing an array.array object for
            # each row.
            pixels = imap_(lambda *row: array(arraycode, row),
                       *[iter(self.deinterlace(raw))]*self.width*self.planes)
        else:
            pixels = self.iterboxed(self.iterstraight(raw))
        meta = dict()
        for attr in 'greyscale alpha planes bitdepth interlace'.split():
            meta[attr] = getattr(self, attr)
        meta['size'] = (self.width, self.height)
        for attr in 'gamma transparent background'.split():
            a = getattr(self, attr, None)
            if a is not None:
                meta[attr] = a
        return self.width, self.height, pixels, meta


    def read_flat(self):
        """
        Read a PNG file and decode it into flat row flat pixel format.
        Returns (*width*, *height*, *pixels*, *metadata*).

        May use excessive memory.

        `pixels` are returned in flat row flat pixel format.

        See also the :meth:`read` method which returns pixels in the
        more stream-friendly boxed row flat pixel format.
        """

        x, y, pixel, meta = self.read()
        arraycode = 'BH'[meta['bitdepth']>8]
        pixel = array(arraycode, itertools.chain(*pixel))
        return x, y, pixel, meta

    def palette(self, alpha='natural'):
        """Returns a palette that is a sequence of 3-tuples or 4-tuples,
        synthesizing it from the ``PLTE`` and ``tRNS`` chunks.  These
        chunks should have already been processed (for example, by
        calling the :meth:`preamble` method).  All the tuples are the
        same size: 3-tuples if there is no ``tRNS`` chunk, 4-tuples when
        there is a ``tRNS`` chunk.  Assumes that the image is colour type
        3 and therefore a ``PLTE`` chunk is required.

        If the `alpha` argument is ``'force'`` then an alpha channel is
        always added, forcing the result to be a sequence of 4-tuples.
        """

        if not self.plte:
            raise FormatError(
                "Required PLTE chunk is missing in colour type 3 image.")
        plte = group(array('B', self.plte), 3)
        if self.trns or alpha == 'force':
            trns = array('B', self.trns or '')
            trns.extend([255]*(len(plte)-len(trns)))
            plte = map(operator.add, plte, group(trns, 1))
        return plte

    def asDirect(self):
        """Returns the image data as a direct representation of an
        ``x * y * planes`` array.  This method is intended to remove the
        need for callers to deal with palettes and transparency
        themselves.  Images with a palette (colour type 3)
        are converted to RGB or RGBA; images with transparency (a
        ``tRNS`` chunk) are converted to LA or RGBA as appropriate.
        When returned in this format the pixel values represent the
        colour value directly without needing to refer to palettes or
        transparency information.

        Like the :meth:`read` method this method returns a 4-tuple:

        (*width*, *height*, *pixels*, *meta*)

        This method normally returns pixel values with the bit depth
        they have in the source image, but when the source PNG has an
        ``sBIT`` chunk it is inspected and can reduce the bit depth of
        the result pixels; pixel values will be reduced according to
        the bit depth specified in the ``sBIT`` chunk (PNG nerds should
        note a single result bit depth is used for all channels; the
        maximum of the ones specified in the ``sBIT`` chunk.  An RGB565
        image will be rescaled to 6-bit RGB666).

        The *meta* dictionary that is returned reflects the `direct`
        format and not the original source image.  For example, an RGB
        source image with a ``tRNS`` chunk to represent a transparent
        colour, will have ``planes=3`` and ``alpha=False`` for the
        source image, but the *meta* dictionary returned by this method
        will have ``planes=4`` and ``alpha=True`` because an alpha
        channel is synthesized and added.

        *pixels* is the pixel data in boxed row flat pixel format (just
        like the :meth:`read` method).

        All the other aspects of the image data are not changed.
        """

        self.preamble()

        # Simple case, no conversion necessary.
        if not self.colormap and not self.trns and not self.sbit:
            return self.read()

        x,y,pixels,meta = self.read()

        if self.colormap:
            meta['colormap'] = False
            meta['alpha'] = bool(self.trns)
            meta['bitdepth'] = 8
            meta['planes'] = 3 + bool(self.trns)
            plte = self.palette()
            def iterpal(pixels):
                for row in pixels:
                    row = map(plte.__getitem__, row)
                    yield array('B', itertools.chain(*row))
            pixels = iterpal(pixels)
        elif self.trns:
            # It would be nice if there was some reasonable way of doing
            # this without generating a whole load of intermediate tuples.
            # But tuples does seem like the easiest way, with no other way
            # clearly much simpler or much faster.  (Actually, the L to LA
            # conversion could perhaps go faster (all those 1-tuples!), but
            # I still wonder whether the code proliferation is worth it)
            it = self.transparent
            maxval = 2**meta['bitdepth']-1
            planes = meta['planes']
            meta['alpha'] = True
            meta['planes'] += 1
            typecode = 'BH'[meta['bitdepth']>8]
            def itertrns(pixels):
                for row in pixels:
                    # For each row we group it into pixels, then form a
                    # characterisation vector that says whether each pixel
                    # is opaque or not.  Then we convert True/False to
                    # 0/maxval (by multiplication), and add it as the extra
                    # channel.
                    row = group(row, planes)
                    opa = map(it.__ne__, row)
                    opa = map(maxval.__mul__, opa)
                    opa = zip(opa) # convert to 1-tuples
                    yield array(typecode,
                      itertools.chain(*map(operator.add, row, opa)))
            pixels = itertrns(pixels)
        targetbitdepth = None
        if self.sbit:
            sbit = struct.unpack('%dB' % len(self.sbit), self.sbit)
            targetbitdepth = max(sbit)
            if targetbitdepth > meta['bitdepth']:
                raise Error('sBIT chunk %r exceeds bitdepth %d' %
                    (sbit,self.bitdepth))
            if min(sbit) <= 0:
                raise Error('sBIT chunk %r has a 0-entry' % sbit)
            if targetbitdepth == meta['bitdepth']:
                targetbitdepth = None
        if targetbitdepth:
            shift = meta['bitdepth'] - targetbitdepth
            meta['bitdepth'] = targetbitdepth
            def itershift(pixels):
                for row in pixels:
                    yield map(shift.__rrshift__, row)
            pixels = itershift(pixels)
        return x,y,pixels,meta

    def asFloat(self, maxval=1.0):
        """Return image pixels as per :meth:`asDirect` method, but scale
        all pixel values to be floating point values between 0.0 and
        *maxval*.
        """

        x,y,pixels,info = self.asDirect()
        sourcemaxval = 2**info['bitdepth']-1
        del info['bitdepth']
        info['maxval'] = float(maxval)
        factor = float(maxval)/float(sourcemaxval)
        def iterfloat():
            for row in pixels:
                yield map(factor.__mul__, row)
        return x,y,iterfloat(),info

    def _as_rescale(self, get, targetbitdepth):
        """Helper used by :meth:`asRGB8` and :meth:`asRGBA8`."""

        width,height,pixels,meta = get()
        maxval = 2**meta['bitdepth'] - 1
        targetmaxval = 2**targetbitdepth - 1
        factor = float(targetmaxval) / float(maxval)
        meta['bitdepth'] = targetbitdepth
        def iterscale():
            for row in pixels:
                yield map(lambda x: int(round(x*factor)), row)
        return width, height, iterscale(), meta

    def asRGB8(self):
        """Return the image data as an RGB pixels with 8-bits per
        sample.  This is like the :meth:`asRGB` method except that
        this method additionally rescales the values so that they
        are all between 0 and 255 (8-bit).  In the case where the
        source image has a bit depth < 8 the transformation preserves
        all the information; where the source image has bit depth
        > 8, then rescaling to 8-bit values loses precision.  No
        dithering is performed.  Like :meth:`asRGB`, an alpha channel
        in the source image will raise an exception.

        This function returns a 4-tuple:
        (*width*, *height*, *pixels*, *metadata*).
        *width*, *height*, *metadata* are as per the :meth:`read` method.

        *pixels* is the pixel data in boxed row flat pixel format.
        """

        return self._as_rescale(self.asRGB, 8)

    def asRGBA8(self):
        """Return the image data as RGBA pixels with 8-bits per
        sample.  This method is similar to :meth:`asRGB8` and
        :meth:`asRGBA`:  The result pixels have an alpha channel, *and*
        values are rescaled to the range 0 to 255.  The alpha channel is
        synthesized if necessary (with a small speed penalty).
        """

        return self._as_rescale(self.asRGBA, 8)

    def asRGB(self):
        """Return image as RGB pixels.  RGB colour images are passed
        through unchanged; greyscales are expanded into RGB
        triplets (there is a small speed overhead for doing this).

        An alpha channel in the source image will raise an
        exception.

        The return values are as for the :meth:`read` method
        except that the *metadata* reflect the returned pixels, not the
        source image.  In particular, for this method
        ``metadata['greyscale']`` will be ``False``.
        """

        width,height,pixels,meta = self.asDirect()
        if meta['alpha']:
            raise Error("will not convert image with alpha channel to RGB")
        if not meta['greyscale']:
            return width,height,pixels,meta
        meta['greyscale'] = False
        typecode = 'BH'[meta['bitdepth'] > 8]
        def iterrgb():
            for row in pixels:
                a = array(typecode, [0]) * 3 * width
                for i in range(3):
                    a[i::3] = row
                yield a
        return width,height,iterrgb(),meta

    def asRGBA(self):
        """Return image as RGBA pixels.  Greyscales are expanded into
        RGB triplets; an alpha channel is synthesized if necessary.
        The return values are as for the :meth:`read` method
        except that the *metadata* reflect the returned pixels, not the
        source image.  In particular, for this method
        ``metadata['greyscale']`` will be ``False``, and
        ``metadata['alpha']`` will be ``True``.
        """

        width,height,pixels,meta = self.asDirect()
        if meta['alpha'] and not meta['greyscale']:
            return width,height,pixels,meta
        typecode = 'BH'[meta['bitdepth'] > 8]
        maxval = 2**meta['bitdepth'] - 1
        def newarray():
            return array(typecode, [0]) * 4 * width
        if meta['alpha'] and meta['greyscale']:
            # LA to RGBA
            def convert():
                for row in pixels:
                    # Create a fresh target row, then copy L channel
                    # into first three target channels, and A channel
                    # into fourth channel.
                    a = newarray()
                    for i in range(3):
                        a[i::4] = row[0::2]
                    a[3::4] = row[1::2]
                    yield a
        elif meta['greyscale']:
            # L to RGBA
            def convert():
                for row in pixels:
                    a = newarray()
                    for i in range(3):
                        a[i::4] = row
                    a[3::4] = array(typecode, [maxval]) * width
                    yield a
        else:
            assert not meta['alpha'] and not meta['greyscale']
            # RGB to RGBA
            def convert():
                for row in pixels:
                    a = newarray()
                    for i in range(3):
                        a[i::4] = row[i::3]
                    a[3::4] = array(typecode, [maxval]) * width
                    yield a
        meta['alpha'] = True
        meta['greyscale'] = False
        return width,height,convert(),meta


# === Legacy Version Support ===

# :pyver:old:  PyPNG works on Python versions 2.3 and 2.2, but not
# without some awkward problems.  Really PyPNG works on Python 2.4 (and
# above); it works on Pythons 2.3 and 2.2 by virtue of fixing up
# problems here.  It's a bit ugly (which is why it's hidden down here).
#
# Generally the strategy is one of pretending that we're running on
# Python 2.4 (or above), and patching up the library support on earlier
# versions so that it looks enough like Python 2.4.  When it comes to
# Python 2.2 there is one thing we cannot patch: extended slices
# http://www.python.org/doc/2.3/whatsnew/section-slices.html.
# Instead we simply declare that features that are implemented using
# extended slices will not work on Python 2.2.
#
# In order to work on Python 2.3 we fix up a recurring annoyance involving
# the array type.  In Python 2.3 an array cannot be initialised with an
# array, and it cannot be extended with a list (or other sequence).
# Both of those are repeated issues in the code.  Whilst I would not
# normally tolerate this sort of behaviour, here we "shim" a replacement
# for array into place (and hope no-ones notices).  You never read this.
#
# In an amusing case of warty hacks on top of warty hacks... the array
# shimming we try and do only works on Python 2.3 and above (you can't
# subclass array.array in Python 2.2).  So to get it working on Python
# 2.2 we go for something much simpler and (probably) way slower.
try:
    array('B').extend([])
    array('B', array('B'))
except:
    # Expect to get here on Python 2.3
    try:
        class _array_shim(array):
            true_array = array
            def __new__(cls, typecode, init=None):
                super_new = super(_array_shim, cls).__new__
                it = super_new(cls, typecode)
                if init is None:
                    return it
                it.extend(init)
                return it
            def extend(self, extension):
                super_extend = super(_array_shim, self).extend
                if isinstance(extension, self.true_array):
                    return super_extend(extension)
                if not isinstance(extension, (list, str)):
                    # Convert to list.  Allows iterators to work.
                    extension = list(extension)
                return super_extend(self.true_array(self.typecode, extension))
        array = _array_shim
    except:
        # Expect to get here on Python 2.2
        def array(typecode, init=()):
            if type(init) == str:
                return map(ord, init)
            return list(init)

# Further hacks to get it limping along on Python 2.2
try:
    enumerate
except:
    def enumerate(seq):
        i=0
        for x in seq:
            yield i,x
            i += 1

try:
    reversed
except:
    def reversed(l):
        l = list(l)
        l.reverse()
        for x in l:
            yield x

try:
    itertools
except:
    class _dummy_itertools:
        pass
    itertools = _dummy_itertools()
    def _itertools_imap(f, seq):
        for x in seq:
            yield f(x)
    itertools.imap = _itertools_imap
    def _itertools_chain(*iterables):
        for it in iterables:
            for element in it:
                yield element
    itertools.chain = _itertools_chain



# === Internal Test Support ===

# This section comprises the tests that are internally validated (as
# opposed to tests which produce output files that are externally
# validated).  Primarily they are unittests.

# Note that it is difficult to internally validate the results of
# writing a PNG file.  The only thing we can do is read it back in
# again, which merely checks consistency, not that the PNG file we
# produce is valid.

# Run the tests from the command line:
# python -c 'import png;png.test()'

# (For an in-memory binary file IO object) We use BytesIO where
# available, otherwise we use StringIO, but name it BytesIO.
try:
    from io import BytesIO
except:
    from StringIO import StringIO as BytesIO
import tempfile
# http://www.python.org/doc/2.4.4/lib/module-unittest.html
import unittest


def test():
    unittest.main(__name__)

def topngbytes(name, rows, x, y, **k):
    """Convenience function for creating a PNG file "in memory" as a
    string.  Creates a :class:`Writer` instance using the keyword arguments,
    then passes `rows` to its :meth:`Writer.write` method.  The resulting
    PNG file is returned as a string.  `name` is used to identify the file for
    debugging.
    """

    import os

    print (name)
    f = BytesIO()
    w = Writer(x, y, **k)
    w.write(f, rows)
    if os.environ.get('PYPNG_TEST_TMP'):
        w = open(name, 'wb')
        w.write(f.getvalue())
        w.close()
    return f.getvalue()

def testWithIO(inp, out, f):
    """Calls the function `f` with ``sys.stdin`` changed to `inp`
    and ``sys.stdout`` changed to `out`.  They are restored when `f`
    returns.  This function returns whatever `f` returns.
    """

    import os

    try:
        oldin,sys.stdin = sys.stdin,inp
        oldout,sys.stdout = sys.stdout,out
        x = f()
    finally:
        sys.stdin = oldin
        sys.stdout = oldout
    if os.environ.get('PYPNG_TEST_TMP') and hasattr(out,'getvalue'):
        name = mycallersname()
        if name:
            w = open(name+'.png', 'wb')
            w.write(out.getvalue())
            w.close()
    return x

def mycallersname():
    """Returns the name of the caller of the caller of this function
    (hence the name of the caller of the function in which
    "mycallersname()" textually appears).  Returns None if this cannot
    be determined."""

    # http://docs.python.org/library/inspect.html#the-interpreter-stack
    import inspect

    frame = inspect.currentframe()
    if not frame:
        return None
    frame_,filename_,lineno_,funname,linelist_,listi_ = (
      inspect.getouterframes(frame)[2])
    return funname

def seqtobytes(s):
    """Convert a sequence of integers to a *bytes* instance.  Good for
    plastering over Python 2 / Python 3 cracks.
    """

    return strtobytes(''.join(chr(x) for x in s))

class Test(unittest.TestCase):
    # This member is used by the superclass.  If we don't define a new
    # class here then when we use self.assertRaises() and the PyPNG code
    # raises an assertion then we get no proper traceback.  I can't work
    # out why, but defining a new class here means we get a proper
    # traceback.
    class failureException(Exception):
        pass

    def helperLN(self, n):
        mask = (1 << n) - 1
        # Use small chunk_limit so that multiple chunk writing is
        # tested.  Making it a test for Issue 20.
        w = Writer(15, 17, greyscale=True, bitdepth=n, chunk_limit=99)
        f = BytesIO()
        w.write_array(f, array('B', map(mask.__and__, range(1, 256))))
        r = Reader(bytes=f.getvalue())
        x,y,pixels,meta = r.read()
        self.assertEqual(x, 15)
        self.assertEqual(y, 17)
        self.assertEqual(list(itertools.chain(*pixels)),
                         map(mask.__and__, range(1,256)))
    def testL8(self):
        return self.helperLN(8)
    def testL4(self):
        return self.helperLN(4)
    def testL2(self):
        "Also tests asRGB8."
        w = Writer(1, 4, greyscale=True, bitdepth=2)
        f = BytesIO()
        w.write_array(f, array('B', range(4)))
        r = Reader(bytes=f.getvalue())
        x,y,pixels,meta = r.asRGB8()
        self.assertEqual(x, 1)
        self.assertEqual(y, 4)
        for i,row in enumerate(pixels):
            self.assertEqual(len(row), 3)
            self.assertEqual(list(row), [0x55*i]*3)
    def testP2(self):
        "2-bit palette."
        a = (255,255,255)
        b = (200,120,120)
        c = (50,99,50)
        w = Writer(1, 4, bitdepth=2, palette=[a,b,c])
        f = BytesIO()
        w.write_array(f, array('B', (0,1,1,2)))
        r = Reader(bytes=f.getvalue())
        x,y,pixels,meta = r.asRGB8()
        self.assertEqual(x, 1)
        self.assertEqual(y, 4)
        self.assertEqual(list(pixels), map(list, [a, b, b, c]))
    def testPtrns(self):
        "Test colour type 3 and tRNS chunk (and 4-bit palette)."
        a = (50,99,50,50)
        b = (200,120,120,80)
        c = (255,255,255)
        d = (200,120,120)
        e = (50,99,50)
        w = Writer(3, 3, bitdepth=4, palette=[a,b,c,d,e])
        f = BytesIO()
        w.write_array(f, array('B', (4, 3, 2, 3, 2, 0, 2, 0, 1)))
        r = Reader(bytes=f.getvalue())
        x,y,pixels,meta = r.asRGBA8()
        self.assertEqual(x, 3)
        self.assertEqual(y, 3)
        c = c+(255,)
        d = d+(255,)
        e = e+(255,)
        boxed = [(e,d,c),(d,c,a),(c,a,b)]
        flat = map(lambda row: itertools.chain(*row), boxed)
        self.assertEqual(map(list, pixels), map(list, flat))
    def testRGBtoRGBA(self):
        "asRGBA8() on colour type 2 source."""
        # Test for Issue 26
        r = Reader(bytes=_pngsuite['basn2c08'])
        x,y,pixels,meta = r.asRGBA8()
        # Test the pixels at row 9 columns 0 and 1.
        row9 = list(pixels)[9]
        self.assertEqual(row9[0:8],
                         [0xff, 0xdf, 0xff, 0xff, 0xff, 0xde, 0xff, 0xff])
    def testLtoRGBA(self):
        "asRGBA() on grey source."""
        # Test for Issue 60
        r = Reader(bytes=_pngsuite['basi0g08'])
        x,y,pixels,meta = r.asRGBA()
        row9 = list(list(pixels)[9])
        self.assertEqual(row9[0:8],
          [222, 222, 222, 255, 221, 221, 221, 255])
    def testCtrns(self):
        "Test colour type 2 and tRNS chunk."
        # Test for Issue 25
        r = Reader(bytes=_pngsuite['tbrn2c08'])
        x,y,pixels,meta = r.asRGBA8()
        # I just happen to know that the first pixel is transparent.
        # In particular it should be #7f7f7f00
        row0 = list(pixels)[0]
        self.assertEqual(tuple(row0[0:4]), (0x7f, 0x7f, 0x7f, 0x00))
    def testAdam7read(self):
        """Adam7 interlace reading.
        Specifically, test that for images in the PngSuite that
        have both an interlaced and straightlaced pair that both
        images from the pair produce the same array of pixels."""
        for candidate in _pngsuite:
            if not candidate.startswith('basn'):
                continue
            candi = candidate.replace('n', 'i')
            if candi not in _pngsuite:
                continue
            print ('adam7 read %s' % (candidate,))
            straight = Reader(bytes=_pngsuite[candidate])
            adam7 = Reader(bytes=_pngsuite[candi])
            # Just compare the pixels.  Ignore x,y (because they're
            # likely to be correct?); metadata is ignored because the
            # "interlace" member differs.  Lame.
            straight = straight.read()[2]
            adam7 = adam7.read()[2]
            self.assertEqual(map(list, straight), map(list, adam7))
    def testAdam7write(self):
        """Adam7 interlace writing.
        For each test image in the PngSuite, write an interlaced
        and a straightlaced version.  Decode both, and compare results.
        """
        # Not such a great test, because the only way we can check what
        # we have written is to read it back again.

        for name,bytes in _pngsuite.items():
            # Only certain colour types supported for this test.
            if name[3:5] not in ['n0', 'n2', 'n4', 'n6']:
                continue
            it = Reader(bytes=bytes)
            x,y,pixels,meta = it.read()
            pngi = topngbytes('adam7wn'+name+'.png', pixels,
              x=x, y=y, bitdepth=it.bitdepth,
              greyscale=it.greyscale, alpha=it.alpha,
              transparent=it.transparent,
              interlace=False)
            x,y,ps,meta = Reader(bytes=pngi).read()
            it = Reader(bytes=bytes)
            x,y,pixels,meta = it.read()
            pngs = topngbytes('adam7wi'+name+'.png', pixels,
              x=x, y=y, bitdepth=it.bitdepth,
              greyscale=it.greyscale, alpha=it.alpha,
              transparent=it.transparent,
              interlace=True)
            x,y,pi,meta = Reader(bytes=pngs).read()
            self.assertEqual(map(list, ps), map(list, pi))
    def testPGMin(self):
        """Test that the command line tool can read PGM files."""
        def do():
            return _main(['testPGMin'])
        s = BytesIO()
        s.write(strtobytes('P5 2 2 3\n'))
        s.write(strtobytes('\x00\x01\x02\x03'))
        s.flush()
        s.seek(0)
        o = BytesIO()
        testWithIO(s, o, do)
        r = Reader(bytes=o.getvalue())
        x,y,pixels,meta = r.read()
        self.assertTrue(r.greyscale)
        self.assertEqual(r.bitdepth, 2)
    def testPAMin(self):
        """Test that the command line tool can read PAM file."""
        def do():
            return _main(['testPAMin'])
        s = BytesIO()
        s.write(strtobytes('P7\nWIDTH 3\nHEIGHT 1\nDEPTH 4\nMAXVAL 255\n'
                'TUPLTYPE RGB_ALPHA\nENDHDR\n'))
        # The pixels in flat row flat pixel format
        flat =  [255,0,0,255, 0,255,0,120, 0,0,255,30]
        asbytes = seqtobytes(flat)
        s.write(asbytes)
        s.flush()
        s.seek(0)
        o = BytesIO()
        testWithIO(s, o, do)
        r = Reader(bytes=o.getvalue())
        x,y,pixels,meta = r.read()
        self.assertTrue(r.alpha)
        self.assertTrue(not r.greyscale)
        self.assertEqual(list(itertools.chain(*pixels)), flat)
    def testLA4(self):
        """Create an LA image with bitdepth 4."""
        bytes = topngbytes('la4.png', [[5, 12]], 1, 1,
          greyscale=True, alpha=True, bitdepth=4)
        sbit = Reader(bytes=bytes).chunk('sBIT')[1]
        self.assertEqual(sbit, strtobytes('\x04\x04'))
    def testPNMsbit(self):
        """Test that PNM files can generates sBIT chunk."""
        def do():
            return _main(['testPNMsbit'])
        s = BytesIO()
        s.write(strtobytes('P6 8 1 1\n'))
        for pixel in range(8):
            s.write(struct.pack('<I', (0x4081*pixel)&0x10101)[:3])
        s.flush()
        s.seek(0)
        o = BytesIO()
        testWithIO(s, o, do)
        r = Reader(bytes=o.getvalue())
        sbit = r.chunk('sBIT')[1]
        self.assertEqual(sbit, strtobytes('\x01\x01\x01'))
    def testLtrns0(self):
        """Create greyscale image with tRNS chunk."""
        return self.helperLtrns(0)
    def testLtrns1(self):
        """Using 1-tuple for transparent arg."""
        return self.helperLtrns((0,))
    def helperLtrns(self, transparent):
        """Helper used by :meth:`testLtrns*`."""
        pixels = zip([0x00, 0x38, 0x4c, 0x54, 0x5c, 0x40, 0x38, 0x00])
        o = BytesIO()
        w = Writer(8, 8, greyscale=True, bitdepth=1, transparent=transparent)
        w.write_packed(o, pixels)
        r = Reader(bytes=o.getvalue())
        x,y,pixels,meta = r.asDirect()
        self.assertTrue(meta['alpha'])
        self.assertTrue(meta['greyscale'])
        self.assertEqual(meta['bitdepth'], 1)
    def testWinfo(self):
        """Test the dictionary returned by a `read` method can be used
        as args for :meth:`Writer`.
        """
        r = Reader(bytes=_pngsuite['basn2c16'])
        info = r.read()[3]
        w = Writer(**info)
    def testPackedIter(self):
        """Test iterator for row when using write_packed.

        Indicative for Issue 47.
        """
        w = Writer(16, 2, greyscale=True, alpha=False, bitdepth=1)
        o = BytesIO()
        w.write_packed(o, [itertools.chain([0x0a], [0xaa]),
                           itertools.chain([0x0f], [0xff])])
        r = Reader(bytes=o.getvalue())
        x,y,pixels,info = r.asDirect()
        pixels = list(pixels)
        self.assertEqual(len(pixels), 2)
        self.assertEqual(len(pixels[0]), 16)
    def testInterlacedArray(self):
        """Test that reading an interlaced PNG yields each row as an
        array."""
        r = Reader(bytes=_pngsuite['basi0g08'])
        list(r.read()[2])[0].tostring
    def testTrnsArray(self):
        """Test that reading a type 2 PNG with tRNS chunk yields each
        row as an array (using asDirect)."""
        r = Reader(bytes=_pngsuite['tbrn2c08'])
        list(r.asDirect()[2])[0].tostring

    # Invalid file format tests.  These construct various badly
    # formatted PNG files, then feed them into a Reader.  When
    # everything is working properly, we should get FormatError
    # exceptions raised.
    def testEmpty(self):
        """Test empty file."""

        r = Reader(bytes='')
        self.assertRaises(FormatError, r.asDirect)
    def testSigOnly(self):
        """Test file containing just signature bytes."""

        r = Reader(bytes=_signature)
        self.assertRaises(FormatError, r.asDirect)
    def testExtraPixels(self):
        """Test file that contains too many pixels."""

        def eachchunk(chunk):
            if chunk[0] != 'IDAT':
                return chunk
            data = zlib.decompress(chunk[1])
            data += strtobytes('\x00garbage')
            data = zlib.compress(data)
            chunk = (chunk[0], data)
            return chunk
        self.assertRaises(FormatError, self.helperFormat, eachchunk)
    def testNotEnoughPixels(self):
        def eachchunk(chunk):
            if chunk[0] != 'IDAT':
                return chunk
            # Remove last byte.
            data = zlib.decompress(chunk[1])
            data = data[:-1]
            data = zlib.compress(data)
            return (chunk[0], data)
        self.assertRaises(FormatError, self.helperFormat, eachchunk)
    def helperFormat(self, f):
        r = Reader(bytes=_pngsuite['basn0g01'])
        o = BytesIO()
        def newchunks():
            for chunk in r.chunks():
                yield f(chunk)
        write_chunks(o, newchunks())
        r = Reader(bytes=o.getvalue())
        return list(r.asDirect()[2])
    def testBadFilter(self):
        def eachchunk(chunk):
            if chunk[0] != 'IDAT':
                return chunk
            data = zlib.decompress(chunk[1])
            # Corrupt the first filter byte
            data = strtobytes('\x99') + data[1:]
            data = zlib.compress(data)
            return (chunk[0], data)
        self.assertRaises(FormatError, self.helperFormat, eachchunk)
    def testFlat(self):
        """Test read_flat."""
        import hashlib

        r = Reader(bytes=_pngsuite['basn0g02'])
        x,y,pixel,meta = r.read_flat()
        d = hashlib.md5(seqtobytes(pixel)).digest()
        self.assertEqual(_enhex(d), '255cd971ab8cd9e7275ff906e5041aa0')
    def testfromarray(self):
        img = from_array([[0, 0x33, 0x66], [0xff, 0xcc, 0x99]], 'L')
        img.save('testfromarray.png')
    def testfromarrayL16(self):
        img = from_array(group(range(2**16), 256), 'L;16')
        img.save('testL16.png')
    def testfromarrayRGB(self):
        img = from_array([[0,0,0, 0,0,1, 0,1,0, 0,1,1],
                          [1,0,0, 1,0,1, 1,1,0, 1,1,1]], 'RGB;1')
        o = BytesIO()
        img.save(o)
    def testfromarrayIter(self):
        import itertools

        i = itertools.islice(itertools.count(10), 20)
        i = imap_(lambda x: [x, x, x], i)
        img = from_array(i, 'RGB;5', dict(height=20))
        f = open('testiter.png', 'wb')
        img.save(f)
        f.close()

    # numpy dependent tests.  These are skipped (with a message to
    # sys.stderr) if numpy cannot be imported.
    def testNumpyuint16(self):
        """numpy uint16."""

        try:
            import numpy
        except ImportError:
            sys.stderr.write("skipping numpy test\n")
            return

        rows = [map(numpy.uint16, range(0,0x10000,0x5555))]
        b = topngbytes('numpyuint16.png', rows, 4, 1,
            greyscale=True, alpha=False, bitdepth=16)
    def testNumpyuint8(self):
        """numpy uint8."""

        try:
            import numpy
        except ImportError:
            sys.stderr.write("skipping numpy test\n")
            return

        rows = [map(numpy.uint8, range(0,0x100,0x55))]
        b = topngbytes('numpyuint8.png', rows, 4, 1,
            greyscale=True, alpha=False, bitdepth=8)
    def testNumpybool(self):
        """numpy bool."""

        try:
            import numpy
        except ImportError:
            sys.stderr.write("skipping numpy test\n")
            return

        rows = [map(numpy.bool, [0,1])]
        b = topngbytes('numpybool.png', rows, 2, 1,
            greyscale=True, alpha=False, bitdepth=1)
    def testNumpyarray(self):
        """numpy array."""
        try:
            import numpy
        except ImportError:
            sys.stderr.write("skipping numpy test\n")
            return

        pixels = numpy.array([[0,0x5555],[0x5555,0xaaaa]], numpy.uint16)
        img = from_array(pixels, 'L')
        img.save('testnumpyL16.png')

# === Command Line Support ===

def _dehex(s):
    """Liberally convert from hex string to binary string."""
    import re
    import binascii

    # Remove all non-hexadecimal digits
    s = re.sub(r'[^a-fA-F\d]', '', s)
    # binscii.unhexlify works in Python 2 and Python 3 (unlike
    # thing.decode('hex')).
    return binascii.unhexlify(strtobytes(s))
def _enhex(s):
    """Convert from binary string (bytes) to hex string (str)."""

    import binascii

    return bytestostr(binascii.hexlify(s))


def read_pam_header(infile):
    """
    Read (the rest of a) PAM header.  `infile` should be positioned
    immediately after the initial 'P7' line (at the beginning of the
    second line).  Returns are as for `read_pnm_header`.
    """

    # Unlike PBM, PGM, and PPM, we can read the header a line at a time.
    header = dict()
    while True:
        l = infile.readline().strip()
        if l == strtobytes('ENDHDR'):
            break
        if not l:
            raise EOFError('PAM ended prematurely')
        if l[0] == strtobytes('#'):
            continue
        l = l.split(None, 1)
        if l[0] not in header:
            header[l[0]] = l[1]
        else:
            header[l[0]] += strtobytes(' ') + l[1]

    required = ['WIDTH', 'HEIGHT', 'DEPTH', 'MAXVAL']
    required = [strtobytes(x) for x in required]
    WIDTH,HEIGHT,DEPTH,MAXVAL = required
    present = [x for x in required if x in header]
    if len(present) != len(required):
        raise Error('PAM file must specify WIDTH, HEIGHT, DEPTH, and MAXVAL')
    width = int(header[WIDTH])
    height = int(header[HEIGHT])
    depth = int(header[DEPTH])
    maxval = int(header[MAXVAL])
    if (width <= 0 or
        height <= 0 or
        depth <= 0 or
        maxval <= 0):
        raise Error(
          'WIDTH, HEIGHT, DEPTH, MAXVAL must all be positive integers')
    return 'P7', width, height, depth, maxval

def read_pnm_header(infile, supported=('P5','P6')):
    """
    Read a PNM header, returning (format,width,height,depth,maxval).
    `width` and `height` are in pixels.  `depth` is the number of
    channels in the image; for PBM and PGM it is synthesized as 1, for
    PPM as 3; for PAM images it is read from the header.  `maxval` is
    synthesized (as 1) for PBM images.
    """

    # Generally, see http://netpbm.sourceforge.net/doc/ppm.html
    # and http://netpbm.sourceforge.net/doc/pam.html

    supported = [strtobytes(x) for x in supported]

    # Technically 'P7' must be followed by a newline, so by using
    # rstrip() we are being liberal in what we accept.  I think this
    # is acceptable.
    type = infile.read(3).rstrip()
    if type not in supported:
        raise NotImplementedError('file format %s not supported' % type)
    if type == strtobytes('P7'):
        # PAM header parsing is completely different.
        return read_pam_header(infile)
    # Expected number of tokens in header (3 for P4, 4 for P6)
    expected = 4
    pbm = ('P1', 'P4')
    if type in pbm:
        expected = 3
    header = [type]

    # We have to read the rest of the header byte by byte because the
    # final whitespace character (immediately following the MAXVAL in
    # the case of P6) may not be a newline.  Of course all PNM files in
    # the wild use a newline at this point, so it's tempting to use
    # readline; but it would be wrong.
    def getc():
        c = infile.read(1)
        if not c:
            raise Error('premature EOF reading PNM header')
        return c

    c = getc()
    while True:
        # Skip whitespace that precedes a token.
        while c.isspace():
            c = getc()
        # Skip comments.
        while c == '#':
            while c not in '\n\r':
                c = getc()
        if not c.isdigit():
            raise Error('unexpected character %s found in header' % c)
        # According to the specification it is legal to have comments
        # that appear in the middle of a token.
        # This is bonkers; I've never seen it; and it's a bit awkward to
        # code good lexers in Python (no goto).  So we break on such
        # cases.
        token = strtobytes('')
        while c.isdigit():
            token += c
            c = getc()
        # Slight hack.  All "tokens" are decimal integers, so convert
        # them here.
        header.append(int(token))
        if len(header) == expected:
            break
    # Skip comments (again)
    while c == '#':
        while c not in '\n\r':
            c = getc()
    if not c.isspace():
        raise Error('expected header to end with whitespace, not %s' % c)

    if type in pbm:
        # synthesize a MAXVAL
        header.append(1)
    depth = (1,3)[type == strtobytes('P6')]
    return header[0], header[1], header[2], depth, header[3]

def write_pnm(file, width, height, pixels, meta):
    """Write a Netpbm PNM/PAM file."""

    bitdepth = meta['bitdepth']
    maxval = 2**bitdepth - 1
    # Rudely, the number of image planes can be used to determine
    # whether we are L (PGM), LA (PAM), RGB (PPM), or RGBA (PAM).
    planes = meta['planes']
    # Can be an assert as long as we assume that pixels and meta came
    # from a PNG file.
    assert planes in (1,2,3,4)
    if planes in (1,3):
        if 1 == planes:
            # PGM
            # Could generate PBM if maxval is 1, but we don't (for one
            # thing, we'd have to convert the data, not just blat it
            # out).
            fmt = 'P5'
        else:
            # PPM
            fmt = 'P6'
        file.write('%s %d %d %d\n' % (fmt, width, height, maxval))
    if planes in (2,4):
        # PAM
        # See http://netpbm.sourceforge.net/doc/pam.html
        if 2 == planes:
            tupltype = 'GRAYSCALE_ALPHA'
        else:
            tupltype = 'RGB_ALPHA'
        file.write('P7\nWIDTH %d\nHEIGHT %d\nDEPTH %d\nMAXVAL %d\n'
                   'TUPLTYPE %s\nENDHDR\n' %
                   (width, height, planes, maxval, tupltype))
    # Values per row
    vpr = planes * width
    # struct format
    fmt = '>%d' % vpr
    if maxval > 0xff:
        fmt = fmt + 'H'
    else:
        fmt = fmt + 'B'
    for row in pixels:
        file.write(struct.pack(fmt, *row))
    file.flush()

def color_triple(color):
    """
    Convert a command line colour value to a RGB triple of integers.
    FIXME: Somewhere we need support for greyscale backgrounds etc.
    """
    if color.startswith('#') and len(color) == 4:
        return (int(color[1], 16),
                int(color[2], 16),
                int(color[3], 16))
    if color.startswith('#') and len(color) == 7:
        return (int(color[1:3], 16),
                int(color[3:5], 16),
                int(color[5:7], 16))
    elif color.startswith('#') and len(color) == 13:
        return (int(color[1:5], 16),
                int(color[5:9], 16),
                int(color[9:13], 16))


def _main(argv):
    """
    Run the PNG encoder with options from the command line.
    """

    # Parse command line arguments
    from optparse import OptionParser
    import re
    version = '%prog ' + re.sub(r'( ?\$|URL: |Rev:)', '', __version__)
    parser = OptionParser(version=version)
    parser.set_usage("%prog [options] [imagefile]")
    parser.add_option('-r', '--read-png', default=False,
                      action='store_true',
                      help='Read PNG, write PNM')
    parser.add_option("-i", "--interlace",
                      default=False, action="store_true",
                      help="create an interlaced PNG file (Adam7)")
    parser.add_option("-t", "--transparent",
                      action="store", type="string", metavar="color",
                      help="mark the specified colour (#RRGGBB) as transparent")
    parser.add_option("-b", "--background",
                      action="store", type="string", metavar="color",
                      help="save the specified background colour")
    parser.add_option("-a", "--alpha",
                      action="store", type="string", metavar="pgmfile",
                      help="alpha channel transparency (RGBA)")
    parser.add_option("-g", "--gamma",
                      action="store", type="float", metavar="value",
                      help="save the specified gamma value")
    parser.add_option("-c", "--compression",
                      action="store", type="int", metavar="level",
                      help="zlib compression level (0-9)")
    parser.add_option("-T", "--test",
                      default=False, action="store_true",
                      help="create a test image (a named PngSuite image if an argument is supplied)")
    parser.add_option('-L', '--list',
                      default=False, action='store_true',
                      help="print list of named test images")
    parser.add_option("-R", "--test-red",
                      action="store", type="string", metavar="pattern",
                      help="test pattern for the red image layer")
    parser.add_option("-G", "--test-green",
                      action="store", type="string", metavar="pattern",
                      help="test pattern for the green image layer")
    parser.add_option("-B", "--test-blue",
                      action="store", type="string", metavar="pattern",
                      help="test pattern for the blue image layer")
    parser.add_option("-A", "--test-alpha",
                      action="store", type="string", metavar="pattern",
                      help="test pattern for the alpha image layer")
    parser.add_option("-K", "--test-black",
                      action="store", type="string", metavar="pattern",
                      help="test pattern for greyscale image")
    parser.add_option("-d", "--test-depth",
                      default=8, action="store", type="int",
                      metavar='NBITS',
                      help="create test PNGs that are NBITS bits per channel")
    parser.add_option("-S", "--test-size",
                      action="store", type="int", metavar="size",
                      help="width and height of the test image")
    (options, args) = parser.parse_args(args=argv[1:])

    # Convert options
    if options.transparent is not None:
        options.transparent = color_triple(options.transparent)
    if options.background is not None:
        options.background = color_triple(options.background)

    if options.list:
        names = list(_pngsuite)
        names.sort()
        for name in names:
            print (name)
        return

    # Run regression tests
    if options.test:
        return test_suite(options, args)

    # Prepare input and output files
    if len(args) == 0:
        infilename = '-'
        infile = sys.stdin
    elif len(args) == 1:
        infilename = args[0]
        infile = open(infilename, 'rb')
    else:
        parser.error("more than one input file")
    outfile = sys.stdout

    if options.read_png:
        # Encode PNG to PPM
        png = Reader(file=infile)
        width,height,pixels,meta = png.asDirect()
        write_pnm(outfile, width, height, pixels, meta)
    else:
        # Encode PNM to PNG
        format, width, height, depth, maxval = \
          read_pnm_header(infile, ('P5','P6','P7'))
        # When it comes to the variety of input formats, we do something
        # rather rude.  Observe that L, LA, RGB, RGBA are the 4 colour
        # types supported by PNG and that they correspond to 1, 2, 3, 4
        # channels respectively.  So we use the number of channels in
        # the source image to determine which one we have.  We do not
        # care about TUPLTYPE.
        greyscale = depth <= 2
        pamalpha = depth in (2,4)
        supported = map(lambda x: 2**x-1, range(1,17))
        try:
            mi = supported.index(maxval)
        except ValueError:
            raise NotImplementedError(
              'your maxval (%s) not in supported list %s' %
              (maxval, str(supported)))
        bitdepth = mi+1
        writer = Writer(width, height,
                        greyscale=greyscale,
                        bitdepth=bitdepth,
                        interlace=options.interlace,
                        transparent=options.transparent,
                        background=options.background,
                        alpha=bool(pamalpha or options.alpha),
                        gamma=options.gamma,
                        compression=options.compression)
        if options.alpha:
            pgmfile = open(options.alpha, 'rb')
            format, awidth, aheight, adepth, amaxval = \
              read_pnm_header(pgmfile, 'P5')
            if amaxval != '255':
                raise NotImplementedError(
                  'maxval %s not supported for alpha channel' % amaxval)
            if (awidth, aheight) != (width, height):
                raise ValueError("alpha channel image size mismatch"
                                 " (%s has %sx%s but %s has %sx%s)"
                                 % (infilename, width, height,
                                    options.alpha, awidth, aheight))
            writer.convert_ppm_and_pgm(infile, pgmfile, outfile)
        else:
            writer.convert_pnm(infile, outfile)


if __name__ == '__main__':
    try:
        _main(sys.argv)
    except Error:
        e = geterror()
        sys.stderr.write("%s\n" % (e,))
