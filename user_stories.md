# User Stories

As a musician, I want to be able to keep my sheet music organised and well labeled, so it's easy to find.

I should be able to search for music based on: the title, the composer, the date.
The metadata should be gathered automatically, and I should be able to edit it in order to keep it accurate.


# Software Requirements

- Database
- Script to populate database with all files in the directory/sub-directory
    - crawl for metadata online and populate that way
    - use the metadata from the file
    - manually input metadata (least optimal)
- Script to search music
- Metadata requirements
    - Name of composition/collection
    - Opus/Catalog number (can be multiple)
    - Composer
    - Date of first publication
