// ISC license, as libass. Exercise the private bitmap decoder with synthetic slots.
#include "../libass/ass_font.c"
#include <limits.h>
#include <stdio.h>
int main(void) {
    unsigned char pixels[] = {0x80, 0x40};
    struct FT_SizeRec_ size = {0};
    struct FT_FaceRec_ face = {0}; face.size = &size;
    struct FT_GlyphSlotRec_ slot = {0}; slot.face = &face;
    slot.bitmap = (FT_Bitmap){.rows=2,.width=2,.pitch=1,.buffer=pixels,.pixel_mode=FT_PIXEL_MODE_MONO};
    ASS_Outline a = {0}, b = {0};
    assert(bitmap_outline(&a, &slot, 0));
    slot.bitmap.pitch=-1; slot.bitmap.buffer=pixels+1;
    assert(bitmap_outline(&b, &slot, 0));
    assert(a.n_points == 8 && b.n_points == 8);
    assert(a.points[0].x == 0 && b.points[0].x == 64);
    ass_outline_free(&a); ass_outline_free(&b);
    slot.bitmap.pitch=0; assert(!bitmap_outline(&a,&slot,0));
    slot.bitmap.pitch=1; slot.bitmap.buffer=NULL; assert(!bitmap_outline(&a,&slot,0));
    slot.bitmap.buffer=pixels; slot.bitmap.pixel_mode=FT_PIXEL_MODE_GRAY; assert(!bitmap_outline(&a,&slot,0));
    slot.bitmap.pixel_mode=FT_PIXEL_MODE_MONO; slot.bitmap.width=4097; assert(!bitmap_outline(&a,&slot,0));
    slot.bitmap.width=2; slot.bitmap_left=INT_MAX; assert(!bitmap_outline(&a,&slot,0));
    slot.bitmap_left=0; slot.advance.x=LONG_MAX; assert(!bitmap_outline(&a,&slot,DECO_UNDERLINE));
    slot.advance.x=64; size.metrics.ascender=LONG_MAX; assert(!bitmap_outline(&a,&slot,DECO_STRIKETHROUGH));
    size.metrics.ascender=0; slot.bitmap.width=0; slot.bitmap.buffer=NULL;
    assert(bitmap_outline(&a,&slot,0)); ass_outline_free(&a);
    puts("PASS bitmap decoder: negative pitch, empty glyph, format, stride, null buffer, coordinate and metric bounds");
}
