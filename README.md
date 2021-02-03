[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=AG-Labs_timelineAnalyser&metric=alert_status)](https://sonarcloud.io/dashboard?id=AG-Labs_timelineAnalyser)
[![<AG-Labs>](https://circleci.com/gh/AG-Labs/SafariBookmarkSaver.svg?style=svg)](https://circleci.com/gh/AG-Labs/SafariBookmarkSaver)

# timelineAnalyser

Analysis of google maps timeline data in Python, initial commit contains a number of data preprocessing functions no visulations or meaningful output at this time.

Future work: provide a visualsation of % visited at varying granularity; heat map visulation; and suggested places to go based on furthest point from currently visited areas

### Prerequisites

A copy of your Google Maps KML data is required. This can be found in the management section of your Google account, [Google Takeout](https://takeout.google.com/settings/takeout). I dont believe Android collects this data by default anymore due to data protection but can be easily turned on to passively collect GPS information from your device. My data stretches back to 2014.

## Authors

- **Andrew Godley** - _All Work_ - [AG Labs](https://github.com/AG-Labs)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
