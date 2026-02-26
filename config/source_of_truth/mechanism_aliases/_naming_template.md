# NAMING Atom — Mechanism Alias Introduction Template
#
# This template is injected once per book, at the end of Chapter 1's HOOK slot,
# as an additional paragraph. It introduces the mechanism alias so every subsequent
# use of {{MA}} lands with weight.
#
# The renderer pulls naming_moment from the matching mechanism_alias YAML and
# injects it via this template structure.
#
# Template tokens:
#   {{MA}}          — short_form (e.g. "the notification spiral")
#   {{MA_DEF}}      — descriptor sentence
#   {{MA_FULL}}     — the full naming_moment block from the YAML
#
# Rendered form (what appears in Chapter 1 after the HOOK atom):
#
#   [naming_moment text verbatim — already a complete paragraph]
#
#   That's {{MA}}. It will come up a lot in this book. Not because it's
#   the only thing happening — but because it's the thing that's underneath
#   most of what we're going to look at.
#
# Note: the closing two sentences are appended programmatically.
# The naming_moment should NOT include "we call this X" — the renderer adds that.
# The naming_moment ends with the behavior described, not the named.
