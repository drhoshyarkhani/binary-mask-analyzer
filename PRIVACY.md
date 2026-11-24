# Privacy scope

The distribution contains procedural geometric examples and source code only.
Original input filenames and directory paths are not persisted in measurement
reports or the SQLite registry. Generated mask IDs and run IDs are used instead.
The runtime application has no account system, telemetry, network endpoints,
remote database, email sender, or shell/subprocess execution.

Ordinary validation/file-operation errors use a generic message instead of
printing the input path. This is not a promise that every possible unexpected
Python/library error or user-created screenshot is free of local information.
Numeric measurements of a user's private inputs may themselves be sensitive.
Keep user-input reports local unless their release has been authorized.

The prepared distribution contains no Git history. Initialize a fresh repository
from this folder when publishing, rather than importing previous repository
metadata. Explicitly configure the intended public Git author identity before
its first commit; a Git client may otherwise infer a local name and hostname.
The public hosting account and deliberate public author identity remain visible.
