# [Instagram Killer](https://instagram-killer-algorithmic.koyeb.app) (Team 4)

## Overview

**Instagram Killer** is a feature-rich REST API built using the FastAPI framework. The application serves as a platform for users to share, manage, and interact with photos. It emphasizes robust authentication, image manipulation, commenting, and additional functionalities to enhance user experience.


![Logo](https://github.com/KossKokos/Python_Web_Project/blob/main/Instagram_killer/logo/image.png)


## Key Features

### Authentication
- Implements a JWT token-based authentication system.
- Users are categorized into three roles: regular user, moderator, and administrator. The first user is always an administrator.
- Utilizes FastAPI decorators to enforce different levels of access (user, moderator, administrator).

### Photo Management
- Users can upload photos with descriptions (POST).
- Photos can be deleted (DELETE), edited (PUT), and accessed by a unique link (GET).
- Allows adding up to 5 tags per photo. Tags are unique across the application.
- Basic image operations are available using Cloudinary's transformation capabilities.

### Commenting
- Each photo has a comment section where users can add comments.
- Users can edit their comments but cannot delete them.
- Moderators and administrators have the ability to delete comments.
- Comments include creation and update timestamps.

### Additional Functionality

#### User Profile
- Includes a route to view a user's profile based on their unique username.
- Provides information such as name, registration date, and the number of uploaded photos.
- Users can edit their information, and different routes cater to viewing and editing profiles.

#### User Management
- Administrators can deactivate users (ban them). Inactive users cannot log in.

#### Logout Mechanism
- Implements a mechanism to log out users, adding their access tokens to a blacklist.

#### Rating System
- Users can rate photos from 1 to 5 stars.
- Ratings are averaged to calculate the overall rating of a photo.
- Users can rate a photo only once, and they cannot rate their own photos.
- Moderators and administrators can view and delete user ratings.

#### Search and Filtering
- Users can search for photos based on keywords or tags.
- Filter search results by rating or upload date.
- Moderators and administrators can search and filter users who have uploaded photos.

### Testing and Deployment

- Achieves test coverage of over 90% through modular testing.
- Deploys the application to a cloud service, such as Koyeb or Fly.io, for accessibility.

## Project Structure

The project follows a structured organization with directories for database, models, repository, routes, schemas, services, and templates. The codebase leverages PostgreSQL for data storage, SQLAlchemy for database interaction, and FastAPI for building the REST API. Additionally, the project includes detailed documentation with Swagger for ease of use.

**Note:** The project is hosted on a public repository (GitHub, GitLab, or BitBucket) and serves as a valuable addition to the developer's portfolio. Expansion of functionality is encouraged, and any enhancements should be discussed with the mentor to align with project goals.

*This application showcases proficiency in FastAPI, database interaction with PostgreSQL, and comprehensive testing and deployment strategies.*
