#!/bin/bash

echo "🔄 Regenerating website..."
cd www
python3 generate_website.py

echo "📁 Copying files to root directory..."
cd ..
cp www/index.html .
cp www/logo.png .

echo "✅ Website files updated and ready for GitHub Pages!"
echo "🌐 Push to GitHub to trigger automatic deployment"
