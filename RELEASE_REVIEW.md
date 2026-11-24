# Standalone distribution review

Review date: 2026-11-24.

## Included material

This release contains the standalone `mask_analyzer` package, its 33 existing
tests, project documentation, dependency requirements, seven procedural NIfTI
fixtures, and reports calculated from those fixtures. The earlier project tree,
its documents and statistics, and repository histories are excluded.

The runtime source and existing tests are unchanged. Changes in this
distribution concern packaging, the Persian guide, and verification metadata.
The original custom license and attribution notice are preserved byte-for-byte.

## Checks

- All 33 existing tests passed in 4.73 seconds with Python 3.12.14 on Linux,
  using the pinned requirements and a non-interactive plotting backend.
- Every bundled mask was checked against its manifest checksum and independently
  regenerated geometry. Arrays, spatial affines, units, and synthetic description
  labels matched the generator's definitions.
- The example database contains seven rows, all labeled `synthetic`. Their
  measurements match the fixture definitions.
- A scan of distributed filenames and contents found no references to the
  earlier external dataset or its identified release and paper identifiers.
- The reviewed source tree contains no Git history, real-data directories,
  installed environments, installed dependency binaries, or runtime caches.
- The bounded source-and-metadata scan found none of the known owner identifiers,
  local-home paths, or common secret markers checked in this review.
- The runtime Python imports contain no networking or subprocess module.

The dependency and data-origin notices are in `DEPENDENCIES.md` and
`DATA_PROVENANCE.md`. The distribution checksums are in `SHA256SUMS.txt`.

## Rights and scope

`LICENSE` remains the custom Lawful Use and Attribution License, version 1.0;
it is not the MIT license and is not represented as OSI-approved. The supplied
terms describe permitted use, modification, redistribution, attribution, user
responsibility for inputs, and limits on liability subject to applicable law.
No new license choice or expanded warranty is made by this packaging review.

Dependency terms remain separate. This archive imports dependencies through
their APIs and does not distribute installed libraries or binary wheels.

These are technical and documentation checks. They do not establish code
ownership against every possible third-party claim, validate the custom terms
in every jurisdiction, certify future uses, or clear unreviewed input data.
The presence of license text does not establish such a legal conclusion.
GitHub's [licensing guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
also distinguishes license information from legal advice.

## Existing copies and repositories

This release updates the downloadable package. It does not alter folders,
installed environments, published repositories, or earlier commits on another
computer. Extract it into a fresh directory so unrelated files from an older
workspace are not carried into a release.

Removing content from a current working tree does not rewrite older commits.
See GitHub's [repository-history guidance](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).
No history-rewriting or remote repository operation was performed here.
