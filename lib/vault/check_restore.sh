# check to see if we need to restore a backup before initializing a fresh Vault:
if [[ -f "lib/vault/restore.tar.gz" ]]; then
  size="$(wc -c <"lib/vault/restore.tar.gz")"

  if [[ $(($size)) < 50000 ]]; then
    echo -e "🚨🚨🚨 ${RED}BAD RESTORE FILE${DEFAULT} 🚨🚨🚨"
    echo "The backup you are restoring from is less than 50kb in size, which is suspiciously small."
    read -r -p 'Do you want to continue restoring? (y/n) ' choice
    case "$choice" in
      n|N) exit 1;;
      y|Y) exit 0;;
      *) echo 'Response not valid';;
    esac
  fi
fi
