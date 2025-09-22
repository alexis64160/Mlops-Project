# Set script directory
if [ "${ZSH_VERSION+set}" ]; then
  SCRIPT_DIR="${0:A:h}"
elif [ "${BASH_VERSION+set}" ]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
  echo "🛑 Unsupported shell. Use Bash or Zsh." >&2
  return 1
fi

# Resolve DSDC_DIR (ENV > recursive search)
if [ "${DSDC_DIR+set}" ]; then
  if [[ -f "$DSDC_DIR/.dsdc_project_root" ]]; then
    export DSDC_DIR
    return 0
  else
    echo "⚠️ .dsdc_project_root file not found in $DSDC_DIR. Proceeding for recursive search."
  fi
else
  echo  ⚠️ DSDC_DIR is not set: proceeding for recursive search of marker file .dsdc_project_root
fi
DSDC_DIR=$(find_project_root $SCRIPT_DIR)
echo "$DSDC_DIR/.dsdc_project_root"
if [[ -f "$DSDC_DIR/.dsdc_project_root" ]]; then
  echo "🆗 Found marker file at $DSDC_DIR" 
else
  echo "🛑 Error: .dsdc_project_root not found by recursive search: unable to install project. Aborting."
  return 1
fi
export DSDC_DIR

echo "fin script $DSDC_DIR"