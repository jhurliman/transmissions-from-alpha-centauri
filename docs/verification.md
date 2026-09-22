> Historical development record. Current approved v1 artwork and reproduction instructions are in the root README and `docs/release/`. This record does not describe the current deliverable.

# Initial verification

- Both Blender scenes saved successfully with Blender 5.2.1 LTS.
- Both 3840 × 2160 PNG renders completed; rich render inspected directly and graphic render inspected in the browser.
- Exhaustive puzzle-state test passed: all five reachable states preserve prerequisites; locked controls cannot skip steps.
- Browser: unprepared door correctly refuses transfer.
- Browser: lens alignment survives switching to the graphic treatment.
- Browser: console → valve → door after alignment reaches completion.
- Browser: Play again resets all progress; switching back to the rich treatment works.
- Fixed a camera dependency-update issue found in visual QA. All four markers now visibly coincide with their objects. Future scene generation asserts anchors are inside the frame.

Not yet tested: mobile devices, production engine integration, game installation detection, SCI patch compatibility, audio, walking, inventory, or saving. No compatibility with Space Quest is claimed by this prototype.
