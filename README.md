# Authors Haven - A Social platform for the creative at heart.

[![Build Status](https://travis-ci.org/andela/ah-the-immortals-backend.svg?branch=develop)](https://travis-ci.org/andela/ah-the-immortals-backend)
[![Coverage Status](https://coveralls.io/repos/github/andela/ah-the-immortals-backend/badge.svg?branch=develop)](https://coveralls.io/github/andela/ah-the-immortals-backend?branch=develop)
[![Maintainability](https://api.codeclimate.com/v1/badges/a61d851f2a0c0e07d1ac/maintainability)](https://codeclimate.com/github/andela/ah-the-immortals-backend/maintainability)

## Vision

Create a community of like minded authors to foster inspiration and innovation
by leveraging the modern web.

---

## APi swagger documenation

[Link to swagger documention](https://ah-the-immortals-staging.herokuapp.com/api/swagger/)

## API Spec

The preferred JSON object to be returned by the API should be structured as follows:

### Users (for authentication)

```source-json
{
  "user": {
    "email": "jake@jake.jake",
    "token": "jwt.token.here",
    "username": "jake",
    "bio": "I work at statefarm",
    "image": null
  }
}
```

### Profile

```source-json
{
  "profile": {
    "username": "jake",
    "bio": "I work at statefarm",
    "image": "image-link",
    "following": false
  }
}
```

### Single Article

```source-json
{
  "article": {
    "slug": "how-to-train-your-dragon",
    "title": "How to train your dragon",
    "description": "Ever wonder how?",
    "body": "It takes a Jacobian",
    "tagList": ["dragons", "training"],
    "createdAt": "2016-02-18T03:22:56.637Z",
    "updatedAt": "2016-02-18T03:48:35.824Z",
    "favorited": false,
    "favoritesCount": 0,
    "author": {
      "username": "jake",
      "bio": "I work at statefarm",
      "image": "https://i.stack.imgur.com/xHWG8.jpg",
      "following": false
    }
  }
}
```

### Multiple Articles

```source-json
{
  "articles":[{
    "slug": "how-to-train-your-dragon",
    "title": "How to train your dragon",
    "description": "Ever wonder how?",
    "body": "It takes a Jacobian",
    "tagList": ["dragons", "training"],
    "createdAt": "2016-02-18T03:22:56.637Z",
    "updatedAt": "2016-02-18T03:48:35.824Z",
    "favorited": false,
    "favoritesCount": 0,
    "author": {
      "username": "jake",
      "bio": "I work at statefarm",
      "image": "https://i.stack.imgur.com/xHWG8.jpg",
      "following": false
    }
  }, {

    "slug": "how-to-train-your-dragon-2",
    "title": "How to train your dragon 2",
    "description": "So toothless",
    "body": "It a dragon",
    "tagList": ["dragons", "training"],
    "createdAt": "2016-02-18T03:22:56.637Z",
    "updatedAt": "2016-02-18T03:48:35.824Z",
    "favorited": false,
    "favoritesCount": 0,
    "author": {
      "username": "jake",
      "bio": "I work at statefarm",
      "image": "https://i.stack.imgur.com/xHWG8.jpg",
      "following": false
    }
  }],
  "articlesCount": 2
}
```

### Single Comment

```source-json
{
  "comment": {
    "id": 1,
    "createdAt": "2016-02-18T03:22:56.637Z",
    "updatedAt": "2016-02-18T03:22:56.637Z",
    "body": "It takes a Jacobian",
    "author": {
      "username": "jake",
      "bio": "I work at statefarm",
      "image": "https://i.stack.imgur.com/xHWG8.jpg",
      "following": false
    }
  }
}
```

### Multiple Comments

```source-json
{
  "comments": [{
    "id": 1,
    "createdAt": "2016-02-18T03:22:56.637Z",
    "updatedAt": "2016-02-18T03:22:56.637Z",
    "body": "It takes a Jacobian",
    "author": {
      "username": "jake",
      "bio": "I work at statefarm",
      "image": "https://i.stack.imgur.com/xHWG8.jpg",
      "following": false
    }
  }],
  "commentsCount": 1
}
```

### List of Tags

```source-json
{
  "tags": [
    "reactjs",
    "angularjs"
  ]
}
```

### Errors and Status Codes

If a request fails any validations, expect errors in the following format:

```source-json
{
  "errors":{
    "body": [
      "can't be empty"
    ]
  }
}
```

### Other status codes:

401 for Unauthorized requests, when a request requires authentication but it isn't provided

403 for Forbidden requests, when a request may be valid but the user doesn't have permissions to perform the action

404 for Not found requests, when a resource can't be found to fulfill the request

## Endpoints:

### User Login:

`POST /api/users/login`

Example request body:

```source-json
{
    "email": "jake@jake.jake",
    "password": "jakejake"
}
```

No authentication required, returns User data

Required fields: `email`, `password`

### User Registration:

`POST /api/users`

Example request body:

```source-json
{
    "username": "Jacob",
    "email": "jake@jake.jake",
    "password": "jakejake"
}
```
No authentication required, returns User data

Required fields: `email`, `password`, `username`

### User Verification:

`GET /api/users/activate/:token`

No authentication required, verifies user

No additional parameters required

### Social Login:

`POST /api/users/oauth/`

Example request body:

```source-json
Google:

{
    "provider": "google-oauth2",
    "access_token": "ya29.Glv7BiLGfjDIpSy2CcYIvd_GVLDZx"
  }


Facebook:

{
    "provider": "facebook",
    "access_token": "ya29.Glv7BiLGfjDIpSy2CcYIvd_GVLDZx"
  }


Twitter:

{
    "provider": "twitter",
    "access_token": "96930231-n5vX3t965JQoO3KLyzQnOjlhnoKmXKAaQlX4IVmAN",
    "access_token_secret": "X8Gd1GXb7MJcmtPjMezN1UUCgaFP518LCEnHZvaUXOqQo"
  }
```

No authentication required, returns User data

Required fields: `provider`, `access_token` and `access_token_secret` for twitter

### Get Current User

`GET /api/user`

Authentication required, returns a User that's the current user

### Update User

`PUT/PATCH /api/user`

Example request body:

```source-json
{
    "email": "jake@jake.jake",
    "bio": "I like to skateboard",
    "image": "https://i.stack.imgur.com/xHWG8.jpg"
}
```

Authentication required, returns the User

Accepted fields: `email`, `username`, `password`, `image`, `bio`

### Password Reset
`POST /api/users/password/reset/`

Example request body:

```source-json
{
		"email":"codingbrian58@gmail.com"
}
```

No authentication required, returns a token

Required fields: `email`

### Password Reset Confirm
`POST /api/users/password/reset/confirm/:token`

Example request body:

```source-json
{
	"password":"passroneggne2424",
	"password_confirm":"passroneggne2424"
}
```

No authentication required, returns a success message

### Get All Profiles

`GET /api/profiles/`

Authentication optional, returns all Profiles

### Get Profile

`GET /api/profiles/:username`

Authentication optional, returns a Profile

### Update User Profile

`PATCH /api/profiles/:username/`

Authentication required, returns an updated Profile

### Follow user

`POST /api/profiles/:username/follow`

Authentication required

No additional parameters required

### Unfollow user

`DELETE /api/profiles/:username/follow`

Authentication required

No additional parameters required

### Get all Users followed by User

`GET /api/profiles/:username/follow/`

Authentication required

No additional parameters required

### Get all Users following a User

`GET /api/profiles/:username/followers/`

Authentication required

No additional parameters required

### Create Article

`POST /api/articles`

Example request body:

```source-json
{
    "title": "How to train your dragon",
    "description": "Ever wonder how?",
    "body": "You have to believe",
    "tagList": ["reactjs", "angularjs", "dragons"]
}
```

Authentication required, will create and return an Article

Required fields: `title`, `description`, `body`

Optional fields: `tagList` as an array of Strings

### List Articles

`GET /api/articles`

Returns most recent articles globally by default, provide `tag`, `author` or `favorited` query parameter to filter results

Query Parameters:

Filter by tag:

`?tag=AngularJS`

Filter by author:

`?author=jake`

Favorited by user:

`?favorited=jake`

Limit number of articles (default is 20):

`?limit=20`

Offset/skip number of articles (default is 0):

`?offset=0`

Authentication optional, will return multiple articles, ordered by most recent first

### Feed Articles

`GET /api/articles/feed`

Can also take `limit` and `offset` query parameters like List Articles

Authentication required, will return multiple articles created by followed users, ordered by most recent first.

### Get One Article

`GET /api/articles/:slug`

No authentication required, will return single article


### Update Article

`PATCH /api/articles/:slug`

Example request body:

```source-json
{
    "title": "Did you train your dragon?"
}
```

Authentication required, returns the updated Article

Optional fields: `title`, `description`, `body`

The `slug` also gets updated when the `title` is changed

### Delete Article

`DELETE /api/articles/:slug`

Authentication required

### Add Comments to an Article

`POST /api/articles/:slug/comments`

Example request body:

```source-json
{
    "body": "His name was my name too."
}
```

Authentication required, returns the created Comment
Required field: `body`

### Get Comments for an Article

`GET /api/articles/:slug/comments`

Authentication optional, returns multiple comments for specific article

### Get specific Comment for an Article

`GET /api/articles/:slug/comments/:id/`

Authentication optional, returns one comment for specific article

### Update Comment

`PUT /api/articles/:slug/comments/:id/`

Example request body:

```source-json
{
    "body": "Did you train your dragon?"
}
```

Authentication required, returns the updated Comment

### Delete Comment

`DELETE /api/articles/:slug/comments/:id`

Authentication required

### Like a Comment

`POST /api/articles/comments/:id/:vote_type/`

Authentication required, returns the Comment and likes information

vote_type is `like`

id is the Comment id

### Get All Comment History

`GET /api/articles/:slug/comments/:comment/history/`

Authentication required, returns all update history of the comment

### Get Specific Comment History

`GET /api/articles/:slug/comments/:comment/history/:id/`

Authentication required, returns the specified update history of the comment

### Favorite Article

`POST /api/articles/:slug/favorite`

Authentication required, returns the Article

No additional parameters required

### Unfavorite Article

`DELETE /api/articles/:slug/favorite`

Authentication required, returns the Article

No additional parameters required

### Get All Favorites for User

`GET /api/articles/favorites/me/`

Authentication required, returns Favorited Articles

No additional parameters required

### Bookmark Article

`POST /api/articles/{slug}/bookmark/`

Authentication required, returns the Article bookmarked with it's comments

No additional parameters required

### Get All Bookmarks for specific User

`GET /api/article/bookmarks/`

Authentication required, returns Bookmarked Articles

No additional parameters required

### Remove a specific Bookmark

`DELETE /api/articles/bookmark/:slug/`

Authentication required, removes a bookmark

No additional parameters required

### Rate Article

`POST /api/articles/:slug/rate/`

Example request body:

```source-json
{
    "rate": 3
}
```

Authentication required, returns the Article rated with it's the rating information

No additional parameters required

### Share Article

`GET /api/articles/:slug/share/:provider/`

Authentication required, returns a share link with a url to the article

Provider can be `facebook`, `twitter` e.t.c

No additional parameters required

### Like or Dislike an Article

`POST /api/articles/:slug/:vote_type/`

Authentication required, returns the Article liked or disliked

vote_type can be either `like` or `dislike`

No additional parameters required

### Remove vote for an Article

`DELETE /api/articles/:slug/:vote_type/`

Authentication required, returns the Article whose vote has been removed

vote_type can be either `like` or `dislike`

No additional parameters required

### Get Tags

`GET /api/tags`

Authentication optional, returns a list of all tags in the application

### Create Highlight

`POST /api/articles/:slug/highlight/`

Example request body:

```source-json
{
    "field": "body",
    "comment": "Review these words",
    "start_index": 37,
    "end_index": 42

}
```

Authentication required, will return a Highlight

Required fields: `field`, `start_index`, `end_index`
Optional fields: `comment`

### Update Highlight

`PATCH /api/articles/:slug/highlight/:id/`

Example request body:

```source-json
{
    "comment": "Rewrite this section"
}
```

Authentication required, returns the updated Highlight

Update fields: `comment`

### Delete Highlight

`DELETE /api/articles/:slug/highlight/:id/`

Authentication required, Removes Highlight

### Get Highlights
`GET /api/articles/:slug/highlight/`

Authentication required, returns all highlights by the user on an article

No additional parameters required

### Report and Article

`POST /api/article/:slug/escalate/`

Example request body:

```source-json
{  
  "reason": "Plagiarism",
  "description": "The article is plagiarized"
}
```

Authentication required, returns a reported article together with the report

No additional parameters required

### Get Reported Articles

`GET /api/article/escalate/`

Authentication required, Creates a report for an article

Admin required

### Delete Reported Article

`DELETE /api/article/:slug/escalate/`

Authentication required, Deletes reported article

Admin required

### Get All user Notifications

`GET /api/notifications/`

Authentication required, Returns all user notifications

### Get single Notifications

`GET /api/notifications/:id/`

Authentication required, returns single notification

### Get user Notifications Subscriptions

`GET /api/notifications/subscription/`

Authentication required, Returns all notifications sunscriprions by user

### Delete One Notification by user

`DELETE /api/notifications/:id/`

Authentication required, Deletes single notification

### Delete All User Notifications

`DELETE /api/notifications/`

Authentication required, Deletes all user notifications

### Subscribe or Unsubscribe to Notifications

`PATCH /api/notifications/subscription`

Authentication required, Updates user subscription to receive notifications

### Update Subscription to Notifications

`PUT /api/notifications/subscription/`

Authentication required, Updates user subscription to receive notifications

### Get All Unread Notifications

`GET /api/notifications/unread/`

Authentication required, Returns all unread notifications

### Unsubscribe from Email Notifications

`GET /api/notifications/unsubscribe_email/:token/`

Authentication optional, Unsubscribes user from Email notifications


## Local Setup

- First Create python virtual environment

```
 $ virtualenv -p python3 env
```

- Install Requirements

```
 $ pip install -r requirements.txt
```

- Create a .env file in the root folder and set variables as in the .env-example

- Create postgres database

```
 $ psql postgres
 postgres=# CREATE USER your-user WITH PASSWORD 'your-password';
 postgres=# ALTER ROLE your-user SET client_encoding TO 'utf8';
 postgres=# ALTER ROLE your-user SET default_transaction_isolation TO 'read committed';
 postgres=# ALTER ROLE your-user SET timezone TO 'UTC';
 postgres=# CREATE DATABASE your-database-name;
 postgres=# GRANT ALL PRIVILEGES ON DATABASE your-database-name TO your-user;
 postgres=# \q
```

- Source the .env file

```
 $ source .env
```

- Run Migrations

```
 $ python manage.py makemigrations
 $ python manage.py migrate
```

- Run Server

```
 $ python manage.py runserver
```

- Run Tests

```
 $ python manage.py test
```
