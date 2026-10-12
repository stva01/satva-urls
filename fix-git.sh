#!/bin/bash
cd /home/stx/from-windows/Satva/Tech/satva-urls
git rebase --abort 2>/dev/null
git checkout -- redirects.json 2>/dev/null
git status
