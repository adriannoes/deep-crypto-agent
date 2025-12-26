#!/bin/bash
# Script para criar o PR da branch chore/consolidate-config-files

gh pr create \
  --base main \
  --head chore/consolidate-config-files \
  --title "chore: consolidate configuration files into pyproject.toml" \
  --body-file pr_description.md
