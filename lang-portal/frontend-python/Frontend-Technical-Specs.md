# Frontend Technical Specifications

## Pages

### Dashboard '/dashboard'

#### Purpose
This page serves as the default page when a user visits a webapp and provides a summary of learning so far for the user

#### Components
This page contains the following components:
- Last Study Session
    - Shows which last activity was used
    - Shows when the last activity was used(date and/or time)
    - Shows how many rights and wrongs were made in last activity
    - Has a link to the group/lasts session
- Study Progress
    - Total words studied vs entire vocabulary in fraction form eg. 3/124
    - Display a mastery progress in percentage eg. 2%
- Quick Stats
    - Success rate in percentage eg. 80%
    - Total number of study sessions done eg. 4
    - Total active groups eg. 3
    - Study streak in days eg. 4 days
- Starting button
    - Goes to study activities page

#### Needed API Endpoints
- GET /api/dashboard/last_study_session
- GET /api/dashboard/study_progress
- GET /api/dashboard/quick_stats
- GET /api/dashboard/starting_button

### Study Activities Index '/study_activities'

#### Purpose
The purpose of this page is to show a collection of study activities. Each Study activity has its own Thumbnail, its name and gives the options to either launch or view said study activity

#### Components
This page contains the following components:
-Study Activity Card
    - Shows a thumbnail of the study activity
    - The name of the study activity
    - A launch button to take us to the launch page
    - The view buttonn to take us to the view page which gives us information about past study sessions for this study session

#### Needed API Endpoints

- GET /api/study_activities

### Study Activity Show '/study_activities/:id'

#### Purpose
The purpose of this page is to show the details of a particular study activity and its past study session history

#### Components
- Name of Study Activity
- Thumbnail of Study Activity
- Description of Study Activity
- Launch button
- Study Activities Paginated list
    - id
    - group name
    - start time
    - end time (inferred by the last word_revieiw_item submitted)
    - number of review items

#### Needed API endpoints

- GET /api/study_activities/:id
- GET /api/study_activities/:id/study_sessions

### Study Activities Launch '/study_activities:id/launch'

#### Purpose
The purpose of this page is to launch the study activity

#### Components
-name of study activity
-launch form
    - select field for group
    - launch now button

##### Behaviour
After the form is submitted a new tab opens with the study activity based on its URL provided in the database

Also after form is submitted the page will redirect to the studdy session show page

#### Needed API Endpoints

- POST /api/study_activities

### Words Index '/words'

#### Purpose
The purpose of this page is to show all words in our database

#### Components
- Paginated word list
    - Columns
        - Chinese
        - Pinyin
        - English
        - Correct count
        - Wrong Count
    - Pagination with 100 items per page
    - Clicking the chinese word will take us to the word show page

#### Needed API Endpoints

- GET /api/words

### Word Show Page '/words/:id'

#### Purpose
The purpose of this page is to show information about a specific word

#### Components
- Chinese
- Pinyin
- English
- Study Statistics
    - Correct count
    - Wrong Count
- Word Groups
    - shown as a series of pills eg. tags
    - when group name is clicked it will take us to the group show page

#### Needed API Endpoints
- GET /api/words/:id

### Word Groups Index '/groups'

#### Purpose
The purpose of this page is to show a list of groups in our database

#### Components
- Paginated Group List
    - Columns
        - Group Name
        - Word Count
- Clicking on the group name will take us to the group show page

#### Needed API Endpoints
- GET /api/groups

### Group Show '/group/id'

#### Purpose
The purpose of this page is to show information about a specific group 

#### Components
- Group name
- Group Statistics
    - Total Word Count
- Words in Group (Paginated list of words)
    - should use the same components as the words index page
- Study Sessions (Paginated list of Study Sessions)
    - Shouls use the same components as the study sesssions index page

#### Needed API Endpoints
- GET /api/groups/:id (The name and group stats)
- GET /api/groups/:id/words
- GET /api/groups/:id/study_sessions

### Study Sessions Index '/study_sessions'

#### Purpose
The purpose of this page is to show the list of study sessions in our database

#### Components
- Paginated Study Session List
    - Columns
        - ID
        - Activity Name
        - Group Name
        - Start Time
        - End Time
        - Number of Review Items
    - Clicking the study session is will take us to the study session show page

#### Needed API Endpoints
- GET /api/study_sessions

### Study Session Show '/study_session/:id' 

#### Purpose
The purpose of this page is to show information about a specific study session

#### Components
- Study Session Details
    - Activity Name
    - Group Name
    - Start Time
    - End Time
- Words review Items (Paginated List of Words)
    -Should use the same component as the words index page

#### Needed API Endpoints
- GET /api/study_sessions/:id
- GET /api/study_sessions/:id/words

### Settings '/settings'

#### Purpose
The purpose of this page is to make configurations to the study portal

#### Components
- Theme Selection eg. Light, Dark, System Default
- Reset History Button
    - this will delete all study sessions and word review button
- Full Reset Button
    - This will drop all tables and re-create with seed data

#### Needed API Endpoints
- POST /api/reset_history
- POST /api/full_reset