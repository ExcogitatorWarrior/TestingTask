# Access Control Overview

We have a few **roles** in the project:

- **Admin** – full access to everything.  
- **Moderator** – can read and update most things, but not delete everything.  
- **User** – can see and work with their own stuff, limited access to others.  
- **Guest** – mostly read-only, can’t change anything.

The project includes a custom authentication system. Users with the `Admin` role have full access to the access-rights differentiation system, which controls permissions across all business elements.

With **business elements** we control access to:

- Users  
- Products  
- Stores
- Orders
- Access Rules  

**Access rules** link roles and elements. For each role, we define what they can do with each element:

- Read / Read all  
- Create  
- Update / Update all  
- Delete / Delete all  

Whenever a user tries to do something:

1. Check their role(s)  
2. Check the rules for that role and element  
3. If allowed then action goes through, otherwise blocked  
4. For object-level actions, `*_all_*` permissions like `read_all_permission` provide access to any business element, while simple permissions like `read_permission` grant access only to elements where the user is the owner.

Everything is stored in the database, so adding new roles, elements, or rules is easy.

## Mock System Example

We provide **mock endpoints** to simulate the real system for testing purposes:

- `/api/mock/users/` → Returns mock users  
- `/api/mock/products/` → Returns mock products  
- `/api/mock/stores/` → Returns mock stores  

These endpoints respect **mock role-based permissions** using `MockRoleBasedPermission`:

### Database Setup & Test Environment

To make the access-control system and mock endpoints work correctly, the project provides multiple ways to prepare the database.

#### 1. Automatic migration with initial data

* We have a migration file:

```
api/migrations/0004_load_initial_data.py
```

* This migration **fills the database with initial roles, business elements, and access rules**.
* Run the usual migrations to apply it:

```bash
python manage.py migrate
```

This ensures the system is ready to use **without manually inserting rules**.

---

#### 2. Manual database setup

* If you want more control, you can use:

```
testing_db_tables.py
```

* This script will **populate the database with access rules manually**.

* If you need to **reset the database**, use:

```
database_drop.py
```

This clears all tables so you can start fresh.

---

#### 3. Docker-based PostgreSQL environment

* For testing purposes, a ready-to-go PostgreSQL environment is provided:

```
postgresql-test-task/docker-compose.yaml
```

* From the `postgresql-test-task` directory, you can start it with:

```bash
docker compose up -d
```

### Functionality Tests

The functionality tests create users with roles in a custom test environment, generate objects in the database related to business elements, and automatically check accessibility based on the rules defined by our access-rights differentiation system.

* To run the tests, use:

```bash
python manage.py test api
```
