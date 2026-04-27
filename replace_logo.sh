#!/usr/bin/env bash
set -euo pipefail

# Usage hint
usage() {
    cat <<EOF
Usage: $(basename "$0") <header|footer> <source-file>

Overwrites one of the Data Portal logo files with <source-file>.

Targets:
  header   src/assets/images/logo.svg        (header logo, 301x119 by default)
  footer   src/assets/images/logo-notext.png (footer logo, 50x63 by default)
EOF
    exit 1
}

if [[ $# -ne 2 ]]; then
    usage
fi

choice=$1
src=$2

# https://stackoverflow.com/a/246128/2148998 -- apparently this is the safest way to get the script directory
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
portal_dir="$script_dir/lib/candig-data-portal/candig-data-portal"

# Figure out what to overwrite
extension="${src##*.}"
case "$choice" in
    header) dest="$portal_dir/src/assets/images/logo.$extension" ;;
    footer) dest="$portal_dir/src/assets/images/logo-notext.$extension" ;;
    -h|--help) usage ;;
    *) echo "Error: unknown target '$choice'" >&2; usage ;;
esac

# Error handling
if [[ ! -f "$src" ]]; then
    echo "Error: source file '$src' does not exist" >&2
    exit 1
fi

# Copy and echo
cp -- "$src" "$dest"
echo "Replaced $dest with $src"

# Make sure the file type of the input is used in the output
case "$choice" in
    header) grep -rl 'images\/logo\.[A-Za-z]\+' $portal_dir | xargs sed -i -e 's/images\/logo\.[a-zA-Z]\+/images\/logo.'$extension'/g' ;;
    footer) grep -rl 'images\/logo-notext\.[A-Za-z]\+' $portal_dir | xargs sed -i -e 's/images\/logo-notext\.[a-zA-Z]\+/images\/logo-notext.'$extension'/g' ;;
esac

# If data-portal is currently running, recompose it
docker ps | grep "candig-data-portal"
if [ $? -eq 0 ]; then
    make recompose-candig-data-portal
fi
