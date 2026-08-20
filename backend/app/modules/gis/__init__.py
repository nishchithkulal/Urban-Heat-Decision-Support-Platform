"""Georeferenced points of interest and spatial queries, backed by PostGIS.

Points only for now (no polygons/rasters) -- the roadmap's "raster/vector processing
as required" is deferred until a concrete feature needs it (CLAUDE.md section 9). The
``geography`` column type (not ``geometry``) is used deliberately: PostGIS computes
``ST_DWithin``/``ST_Distance`` on a geography in meters over the sphere, which is what
"stations within N km" actually means for real-world lat/lon -- a ``geometry`` column
would compute in degrees on a flat plane and give a wrong answer.
"""
