#!/bin/bash
cd /home/stx/from-windows/Satva/Tech/satva-urls
{
echo "=== STATUS ==="
git status
echo "=== LOG ==="
git log --oneline -5
} > git-output.txt 2>&1
