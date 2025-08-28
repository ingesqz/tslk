# TSLK Swimming Club Records v1.6

## 🎉 Major UI and Translation Improvements

### ✨ New Features
- **Simplified Gender Selection**: Replaced dropdown with clean radio buttons (Menn/Kvinner)
- **Gender-Filtered Best Results**: Best results now filter by selected gender
- **Enhanced Translation System**: Complete Norwegian/English translation support
- **Event Name Translations**: All swimming events now translate properly

### 🔧 Improvements
- **Better User Experience**: Cleaner interface with focused gender selection
- **Real-time Filtering**: Best results update immediately when gender changes
- **Bilingual Support**: Full translation for all UI elements and event names
- **Mobile Responsive**: Improved mobile experience with radio buttons

### 🐛 Bug Fixes
- Fixed translation system for radio buttons
- Fixed event name translations in dropdown and results
- Removed broken references to non-existent UI elements
- Restored complete bilingual functionality

### 📊 Technical Changes
- Updated `showBestSwimmers()` to respect gender selection
- Added `eventTranslations` mapping for all swimming events
- Enhanced `changeLanguage()` function with proper event dropdown updates
- Improved filter logic for better user experience

### 🌐 Website Updates
- **GitHub Pages**: https://ingesqz.github.io/tslk
- **Local Testing**: Available in www/index.html

### 📝 Event Translations Added
- 50m/100m/200m Rygg → Backstroke
- 50m/100m/200m Bryst → Breaststroke  
- 50m/100m/200m/400m/800m/1500m Fri → Freestyle
- All other events maintain consistent naming

### 🔄 Recent Changes Summary
1. **Gender Selection UI**: Simplified from dropdown to radio buttons
2. **Best Results Filtering**: Now respects selected gender
3. **Translation System**: Complete overhaul with event name translations
4. **User Experience**: More intuitive and responsive interface

---
**Release Date**: 2025-01-30
**Version**: v1.6
**Status**: ✅ Production Ready

## 🚀 How to Use

1. **Visit the website**: https://ingesqz.github.io/tslk
2. **Select gender**: Use the radio buttons (Menn/Kvinner)
3. **Choose event**: Select from the dropdown (translated names)
4. **View results**: See filtered results based on your selection
5. **Switch language**: Click the flag buttons (🇳🇴/🇬🇧)

## 📁 Files Included
- `www/index.html` - Main website
- `www/generate_website.py` - Website generation script
- `process_all_events.py` - Data processing script
- `deploy.sh` - Deployment script
- All supporting files and data
