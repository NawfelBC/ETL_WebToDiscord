# ETL_WebToDiscord

Built an ETL pipeline project hosted on [Heroku](https://www.heroku.com/) that will scrape a dev jobs website every 2 hours looking if a new internship job has been posted. The data will be then loaded on [Firebase](https://firebase.google.com/) using [Pyrebase](https://github.com/thisbejim/Pyrebase) package. If the new loaded data is different, which means a new job has been posted, it triggers a process that will send a message on a Discord channel to alert user.
