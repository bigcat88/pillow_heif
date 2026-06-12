# Release process

1. Fill in the release date for the version section in `CHANGELOG.md`.
2. Set the version in `pillow_heif/_version.py`, merge to `master`.
3. Optionally run the `Wheels` workflow manually on `master` to pre-validate all builds.
4. Create and push the tag:

   ```console
   git tag v1.X.Y && git push origin v1.X.Y
   ```

5. CI builds all wheels and the sdist, publishes them to PyPI via Trusted Publishing and creates the GitHub release with the changelog section.
6. If a build or upload fails for a transient reason: re-run the failed jobs from the Actions UI, the flow is idempotent.
   If `check-version`, `check-manifest` or the dists count fails, the tagged commit itself is wrong: fix it on `master`, delete the tag and push it again.
7. Set `_version.py` on `master` to the next development version.
