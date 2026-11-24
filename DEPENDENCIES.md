# External software dependencies

This distribution uses public software packages through their APIs. Installed
packages, binary wheels, fonts, and upstream source trees are not bundled.
SQLite support is provided by Python's standard `sqlite3` module.

| Direct dependency | Project license | Official notice |
| --- | --- | --- |
| NumPy | BSD 3-Clause; distributions include additional notices | [License](https://numpy.org/doc/stable/license.html) |
| NiBabel | MIT | [Notice](https://nipy.org/nibabel/legal.html) |
| pandas | BSD 3-Clause | [Notice](https://pandas.pydata.org/docs/getting_started/overview.html#license) |
| Matplotlib | PSF-based Matplotlib license and component notices | [Notice](https://matplotlib.org/stable/project/license.html) |
| pytest | MIT | [Notice](https://docs.pytest.org/en/stable/license.html) |

Installation brings additional dependencies with their own notices. A license
for project code does not replace those terms. If creating a distribution that
bundles installed libraries or binaries, review and retain the component notices
for that distribution separately.
