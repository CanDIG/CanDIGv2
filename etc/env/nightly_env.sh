# Place this script at the CanDIG root folder and setup the lines below to initialize nightly build
# Then, create a crontab to cd into the CanDIG root folder and run nightly_build.sh
export BOT_TOKEN=<BOT_TOKEN>
export HOOK_URL=<HOOK_URL>
export INGEST_PATH=<PATH_TO_CANDIGV2_INGEST>
export BUILD_PATH=<PATH_TO_BUILD>

# Set this to 1 to skip the git pull step, which may destroy changes in your working directories
export SKIP_GIT=0

sed -i "s@KEEP_TEST_DATA=false@KEEP_TEST_DATA=true@" .env
