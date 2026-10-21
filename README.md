DomeD native bitmap experiment
=============================

This separate clone is based on upstream 0.17.4 (`bbb3c7f1570a4a021e52683f3fbdf74fe492ae84`),
branch `experiment/native-bitmap-fonts`. Nothing is installed system-wide.
Enable with `meson setup build-bitmap -Dnative-bitmap-fonts=true -Ddefault_library=shared`;
then `meson compile -C build-bitmap`. The Meson option defaults to false.
Autotools does not enable this experimental path.

The prototype admits non-scalable FreeType faces in Fontconfig and embedded-font
selection, chooses the nearest native strike, uses fixed-strike advances in
HarfBuzz, and converts monochrome glyph runs into pixel-cell contours. Existing
libass transforms, clipping, outline/shadow and glyph caches remain in use.
It reads the actual bitmap strike; no outline companion is substituted. This is
not a new direct GPU renderer: cached contours pass through libass's ordinary CPU
rasterizer, and mpv uploads/composites the resulting masks on its GPU video path.

`test/native-bitmap.py` compares native masks/advances/spacing against FreeType
for bitmap TTF, OTB and PCF using only the embedded test font. It checks nearest
strike selection, unchanged-frame caching, outline/shadow, underline and rotation;
a scalable Noto Sans control is byte-identical with the option disabled/enabled.
Run it with `uv run --no-project --with freetype-py python test/native-bitmap.py`
followed by enabled/disabled shared libraries and the three bitmap-font paths.
`test/native-bitmap-outline.c` exercises negative pitch, empty glyphs, unsupported
pixel modes, short/null buffers and coordinate/metric bounds under ASan/UBSan.
The parent experiment's `artifacts/libass-bitmap*` contains the commands' evidence.

Limitations: only monochrome fixed strikes are supported; grayscale/color strikes,
vertical glyph rotation and synthetic bold/italic are not implemented. Native
sizes snap rather than scaling to arbitrary requested sizes. Transforms can
resample pixel edges; the comparison checks thresholded masks at native size,
not equality of all antialiased alpha values. Complex multilingual shaping,
fallback combinations, karaoke, clipping and the full ASS regression corpus still
need broader testing before deployment. Malformed-font fuzzing remains necessary.
The public ABI is unchanged, but this remains a local prototype, not a release.

The parent `render-desktop-preview.py` accepts `DE_XR_LIBASS_BITMAP=1` to run
mpvr against `build-bitmap/libass` only in an isolated DomeD session. The real
Galmuri14Bitmap OSD proof uses `gpu-next`; default mpvr settings and its separate
symbol font/subtitle font properties are retained.

---

libass [![Coverity scan build status](https://scan.coverity.com/projects/3531/badge.svg)](https://scan.coverity.com/projects/3531) [![Build status](https://github.com/libass/libass/actions/workflows/ghci.yml/badge.svg?branch=master&event=push)](https://github.com/libass/libass/actions/workflows/ghci.yml?query=branch%3Amaster+event%3Apush)
======
libass is a portable subtitle renderer for the ASS/SSA (Advanced Substation Alpha/Substation Alpha) subtitle format. It is mostly compatible with VSFilter.

Get it
======
See [GitHub releases](https://github.com/libass/libass/releases) for the latest release 0.17.4 (released 2025-06-07).
See the [changelog](https://github.com/libass/libass/blob/master/Changelog) for a detailed list of changes.

Source code is available from our [GitHub repository](https://github.com/libass/libass).

Contact
=======
Please use the [issue tracker](https://github.com/libass/libass/issues?state=open) to report bugs or feature requests.

We have an IRC channel, too. Talk to us on [irc.libera.chat/#libass](https://web.libera.chat/#libass). Note that we cannot be online all the time and we cannot answer IRC questions if you leave the channel. Even if you do not get an immediate response, keep your IRC client open, and we will eventually get back to you.

Building
========

libass offers two build systems to choose from: Autotools and Meson.

Autotools is preferred for development since it integrates with our testing
infrastructure and is feature-complete on all platforms supported by Autotools.  
If you are packaging libass for distribution, Autotools is recommended;
when packaging for Windows Meson should work equally well.

Meson lacks integration with testing infrastructure, but works otherwise well on
Windows. It is suited for static-only builds on any platform well supported by
Meson and as a Meson subproject.
Notably, Meson supports MSVC and generation of VS project files.

Macro defines
-------------

Unless developing libass there’s usually no need to manually define macros
and there are no stability guarantees for these manual defines.

- `DEBUG_LEVEL=0..3`
  - `0` use the default set of asserts; implied if macro is not defined at all
  - `1`, `2` *unused*
  - `3` additionally assert assumptions usually pledged to the compiler for optimization purposes

Information about the ASS format:
=================================
- [ASS format overview](https://github.com/libass/libass/wiki/ASS-File-Format-Guide)
- [ASS override tags (Aegisub manual)](http://docs.aegisub.org/latest/ASS_Tags/)
- [VSFilter source code (Guliverkli2)](http://sourceforge.net/p/guliverkli2/code/HEAD/tree/src/subtitles/)

Other ASS/SSA implementations:
==============================
- VSFilter:
  - [xy-VSFilter/XySubFilter](https://github.com/Cyberbeing/xy-VSFilter/)
    - [pfmod](https://github.com/pinterf/xy-VSFilter/)
  - VSFilter in [MPC-HC](https://github.com/clsid2/mpc-hc/tree/develop/src/filters/transform/VSFilter/)
  - [VSFilterMod](https://code.google.com/archive/p/vsfiltermod/) with custom format extensions (defunct, subsumed by forks)
    - [sorayuki fork](https://github.com/sorayuki/VSFilterMod/) with some bugfixes (defunct)
    - various forks focussing on internal use
  - [Threaded VSFilter](https://code.google.com/p/threaded-vsfilter/) (defunct)
  - VSFilter in [Guliverkli2](http://sourceforge.net/projects/guliverkli2/) (defunct, subsumed by all of the above)
  - VSFilter in [guliverkli](http://sourceforge.net/projects/guliverkli/) (defunct, forked as Guliverkli2)
- [ffdshow](http://ffdshow-tryout.sourceforge.net/) (defunct)
- [Perian](https://github.com/MaddTheSane/perian) (defunct)
- [asa](https://web.archive.org/web/20110906033709/http://asa.diac24.net/) (defunct)
- [libjass](https://github.com/Arnavion/libjass) (defunct)
- [ASS.js](https://github.com/weizhenye/ASS)

Packaging status
================

[![Packaging status](https://repology.org/badge/vertical-allrepos/libass.svg?columns=3&header=libass&exclude_unsupported=1)](https://repology.org/project/libass/versions)
