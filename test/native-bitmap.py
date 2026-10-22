#!/usr/bin/env python3
# SPDX-License-Identifier: ISC
"""Compare public ASS_Image output against native FreeType bitmap masks.

uv run --no-project --with freetype-py python test/native-bitmap.py ENABLED_LIB DISABLED_LIB FONT...
Font provider NONE and a single embedded font prevent outline fallback.
"""
import ctypes as C
from pathlib import Path
import sys
import freetype

class Image(C.Structure): pass
Image._fields_ = [('w',C.c_int),('h',C.c_int),('stride',C.c_int),('bitmap',C.POINTER(C.c_ubyte)),
                 ('color',C.c_uint32),('dst_x',C.c_int),('dst_y',C.c_int),('next',C.POINTER(Image)),('type',C.c_int)]

def api(path):
    lib=C.CDLL(str(Path(path).resolve()))
    for name,args,result in [
        ('ass_library_init',[],C.c_void_p),('ass_renderer_init',[C.c_void_p],C.c_void_p),
        ('ass_set_frame_size',[C.c_void_p,C.c_int,C.c_int],None),
        ('ass_set_storage_size',[C.c_void_p,C.c_int,C.c_int],None),
        ('ass_set_fonts',[C.c_void_p,C.c_char_p,C.c_char_p,C.c_int,C.c_char_p,C.c_int],None),
        ('ass_add_font',[C.c_void_p,C.c_char_p,C.c_char_p,C.c_int],None),
        ('ass_read_memory',[C.c_void_p,C.c_char_p,C.c_size_t,C.c_char_p],C.c_void_p),
        ('ass_render_frame',[C.c_void_p,C.c_void_p,C.c_longlong,C.POINTER(C.c_int)],C.POINTER(Image)),
        ('ass_free_track',[C.c_void_p],None),('ass_renderer_done',[C.c_void_p],None),('ass_library_done',[C.c_void_p],None)]:
        fn=getattr(lib,name);fn.argtypes=args;fn.restype=result
    return lib

def render(lib,file,size,text,outline=0,shadow=0):
    face=freetype.Face(str(file));family=face.family_name.decode()
    library=lib.ass_library_init();assert library
    data=Path(file).read_bytes();lib.ass_add_font(library,b'fixture',data,len(data))
    renderer=lib.ass_renderer_init(library);assert renderer
    lib.ass_set_frame_size(renderer,640,240);lib.ass_set_storage_size(renderer,640,240)
    lib.ass_set_fonts(renderer,None,family.encode(),0,None,1)
    script=f'''[Script Info]
ScriptType: v4.00+
PlayResX: 640
PlayResY: 240
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{family},{size},&H00FFFFFF,&H00FFFFFF,&H00FFFFFF,&H00FFFFFF,0,0,0,0,100,100,0,0,1,{outline},{shadow},7,40,40,40,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:10.00,Default,,0,0,0,,{text}
'''.encode()
    track=lib.ass_read_memory(library,script,len(script),None);assert track
    def frame():
        changed=C.c_int();node=lib.ass_render_frame(renderer,track,1000,C.byref(changed));pixels=bytearray(640*240)
        while node:
            im=node.contents
            if im.w and im.h:
                assert im.stride>=im.w and im.w<8192 and im.h<8192
                source=C.string_at(im.bitmap,im.stride*(im.h-1)+im.w)
                for y in range(im.h):
                    for x in range(im.w):
                        X,Y=im.dst_x+x,im.dst_y+y
                        if 0<=X<640 and 0<=Y<240:
                            at=Y*640+X;pixels[at]=max(pixels[at],source[y*im.stride+x])
            node=im.next
        return pixels,changed.value
    try:
        first,_=frame();second,changed=frame();assert first==second and changed==0,'Unchanged glyph cache output'
        return first
    finally:
        lib.ass_free_track(track);lib.ass_renderer_done(renderer);lib.ass_library_done(library)

def crop(pixels,width):
    points=[(i%width,i//width)for i,value in enumerate(pixels)if value>=128]
    if not points:return ()
    x0=min(p[0]for p in points);x1=max(p[0]for p in points)+1
    y0=min(p[1]for p in points);y1=max(p[1]for p in points)+1
    return tuple(tuple(pixels[y*width+x]>=128 for x in range(x0,x1))for y in range(y0,y1))

def reference(file,text):
    face=freetype.Face(str(file));assert not face.is_scalable and face.num_fixed_sizes
    face.select_size(0);glyphs=[];cursor=0
    for char in text:
        face.load_char(char,freetype.FT_LOAD_DEFAULT);g=face.glyph;b=g.bitmap
        if b.width and b.rows:assert b.pixel_mode==freetype.FT_PIXEL_MODE_MONO and b.pitch>0
        glyphs.append((cursor+g.bitmap_left,g.bitmap_top,b.width,b.rows,b.pitch,bytes(b.buffer)))
        cursor+=g.advance.x//64
    pixels=bytearray(640*240)
    for left,top,w,h,pitch,data in glyphs:
        for y in range(h):
            for x in range(w):
                if data[y*pitch+x//8]&(0x80>>(x%8)):pixels[(80-top+y)*640+40+left+x]=255
    return crop(pixels,640),face.available_sizes[0].y_ppem/64

enabled=api(sys.argv[1]);disabled=api(sys.argv[2])
for font in map(Path,sys.argv[3:]):
    for text in ['M','MMMM','M M']:
        expected,size=reference(font,text);actual=render(enabled,font,size,text)
        assert crop(actual,640)==expected,(font,text,'Native glyph mask or advance mismatch')
        assert crop(render(enabled,font,size+7,text),640)==expected,'Closest native strike remains at native size'
        assert not crop(render(disabled,font,size,text),640),'Disabled build must reject bitmap-only embedded fonts'
    assert sum(render(enabled,font,size,'M',1,1))>sum(render(enabled,font,size,'M')),'Outline/shadow pipeline remains available'
    assert crop(render(enabled,font,size,r'{\u1}M'),640),'Underline retains native glyphs'
    assert crop(render(enabled,font,size,r'{\frz15}M'),640),'Rotation retains native glyphs'
    print('PASS native mask, spaces/advances, strike snapping, cache, outline/shadow, underline and rotation:',font.name,flush=True)
outline=Path('/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf')
assert not crop(render(enabled,outline,21,'Outline control'),640), 'BDF-only build accepted an outline font'
assert crop(render(disabled,outline,21,'Outline control'),640), 'Control library must still render the outline fixture'
print('PASS BDF-only build rejects outline fonts; unpatched control still accepts them',flush=True)
