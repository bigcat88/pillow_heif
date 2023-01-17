# The guide to programming cirrus-ci tasks using starlark is found at https://cirrus-ci.org/guide/programming-tasks/
#
# In this simple starlark script we simply check conditions for whether a CI run should go ahead.
# If the conditions are met, then we just return the yaml containing the tasks to be run.

load("cirrus", "env", "fs", "http")

def main(ctx):

    if env.get("CIRRUS_REPO_FULL_NAME") != "bigcat88/pillow_heif":
        return []

    # Obtain commit message for the event. Unfortunately CIRRUS_CHANGE_MESSAGE
    # only contains the actual commit message on a non-PR trigger event.
    # For a PR event it contains the PR title and description.
    SHA = env.get("CIRRUS_CHANGE_IN_REPO")
    url = "https://api.github.com/repos/bigcat88/pillow_heif/git/commits/" + SHA
    dct = http.get(url).json()
    if "[skip cirrus]" in dct["message"] or "[skip ci]" in dct["message"]:
        return []

    # this configuration(default) runs macosx_arm64 builds from source.
    return fs.read("ci/cirrus_general_ci.yml")
