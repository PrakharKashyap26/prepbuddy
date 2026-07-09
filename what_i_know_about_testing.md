# What I Know About Testing (FastAPI + Pytest)

> A self-reference document extracted from my FastAPI project's test suite.

---

## 1. Testing Framework — Pytest

I use **pytest** as my testing framework. Key things I know:

- Test files are prefixed with `test_` (e.g., `test_users.py`, `test_posts.py`).
- Test functions are also prefixed with `test_` so pytest auto-discovers them.
- I run tests with the `pytest` command from the project root.
- Pytest collects and runs all matching test functions automatically.

---

## 2. Project Test Structure

My test suite is organized into focused modules:

| File | What It Tests | # of Tests |
|---|---|---|
| `test_calculations.py` | Pure unit logic (add, subtract, multiply, divide, BankAccount) | 10 |
| `test_users.py` | User registration & login endpoints | 4 |
| `test_posts.py` | Full CRUD on posts (create, read, update, delete) | 13 |
| `test_votes.py` | Voting/un-voting on posts | 6 |
| `conftest.py` | Shared fixtures used across all test files | — |
| `database.py` | Legacy/commented-out DB setup (now consolidated into conftest) | — |

---

## 3. Fixtures (`@pytest.fixture`)

I know that **fixtures** provide reusable setup/teardown logic that gets injected into tests by name.

### Fixtures I've built:

#### `session` — Database session with full table reset
```python
@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)   # tear down old tables
    Base.metadata.create_all(bind=engine)  # create fresh tables
    db = TestingSessionLocal()
    try:
        yield db        # <-- 'yield' makes this a generator fixture
    finally:
        db.close()      # cleanup runs AFTER the test finishes
```
**Key concepts here:**
- `yield` vs `return` — using `yield` lets me run cleanup code *after* the test.
- Every test gets a **completely fresh database** (drop → create → use → close).
- This prevents test pollution where one test's data leaks into another.

#### `client` — FastAPI TestClient with dependency override
```python
@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
```
**Key concepts here:**
- **Dependency Injection Override** — I replace the real `get_db` dependency with a test version that uses my test database session.
- `app.dependency_overrides[get_db]` is FastAPI's mechanism for swapping dependencies during tests.
- The `client` fixture *depends on* `session`, so pytest builds the fixture chain automatically.

#### `test_user` / `test_user2` — Pre-created users
```python
@pytest.fixture
def test_user(client):
    user_data = {"email": "hello123@gmail.com", "password": "password123"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user['password'] = user_data['password']  # attach raw password for login tests
    return new_user
```
**Key concepts here:**
- Fixtures can **call API endpoints** to set up state.
- I attach the plain-text password back onto the response dict so login tests can use it (the API only returns the hashed version).
- Having two users (`test_user`, `test_user2`) lets me test **ownership/authorization boundaries** (e.g., user1 can't delete user2's post).

#### `token` — JWT token generation
```python
@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user['id']})
```
- Generates a valid JWT by calling the app's own `create_access_token` utility.

#### `authorized_client` — Pre-authenticated client
```python
@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client
```
**Key concepts here:**
- Builds on `client` + `token` fixtures — **fixture chaining/composition**.
- Injects the `Authorization` header so every request from this client is authenticated.
- I use `**client.headers` spread to preserve any existing default headers.

#### `test_posts` — Seed data for post tests
```python
@pytest.fixture
def test_posts(test_user, session, test_user2):
    posts_data = [...]
    def create_post_model(post):
        return models.Post(**post)
    post_map = map(create_post_model, posts_data)
    posts = list(post_map)
    session.add_all(posts)
    session.commit()
    posts = session.query(models.Post).all()
    return posts
```
**Key concepts here:**
- Uses `map()` + a helper function to bulk-create model instances.
- `session.add_all()` for batch insertion.
- Re-queries after commit to get the posts with their auto-generated `id` values.
- Includes a post owned by `test_user2` (post index 3) so I can test cross-user authorization.

#### `test_votes` — Seed a vote record
```python
@pytest.fixture()
def test_votes(test_posts, session, test_user):
    new_vote = models.Vote(post_id=test_posts[3].id, user_id=test_user['id'])
    session.add(new_vote)
    session.commit()
```
- Directly creates a database record via the ORM (bypasses the API).

---

## 4. `conftest.py` — Shared Fixture Hub

I know that `conftest.py` is a **special pytest file**:
- Any fixture defined here is **automatically available** to all test files in the same directory (and subdirectories).
- No imports needed — pytest handles discovery.
- This is where I centralize shared setup: DB session, client, users, auth, seed data.

---

## 5. Test Database Isolation

```python
SQLALCHEMY_DATABSE_URL = f"postgresql://...:{settings.database_port}/test_{settings.database_name}"
```

**What I know:**
- I use a **separate test database** (`test_` prefix) so tests never touch production data.
- The connection string is built from `settings` (environment variables via pydantic).
- Tables are **dropped and recreated** before every test via the `session` fixture — full isolation.
- I considered using **Alembic migrations** (`command.upgrade("head")` / `command.downgrade("base")`) but switched to the simpler `create_all` / `drop_all` approach.

---

## 6. FastAPI TestClient

```python
from fastapi.testclient import TestClient
```

**What I know:**
- `TestClient` wraps the FastAPI app and lets me make HTTP requests **without starting a real server**.
- It's built on top of `httpx` / `requests` — same API (`.get()`, `.post()`, `.put()`, `.delete()`).
- I can pass `json={}` for JSON bodies and `data={}` for form-encoded bodies (used for OAuth login).
- Response object gives me `.status_code`, `.json()`, etc.

---

## 7. Parametrized Tests (`@pytest.mark.parametrize`)

I use parametrize to run the **same test logic with multiple inputs**:

### Example 1 — Testing `add()` with multiple values:
```python
@pytest.mark.parametrize("num1, num2, expected", [
    (3, 2, 5),
    (7, 1, 8),
    (12, 4, 16)
])
def test_add(num1, num2, expected):
    assert add(num1, num2) == expected
```

### Example 2 — Testing bank transactions:
```python
@pytest.mark.parametrize("num1, num2, expected", [
    (300, 200, 100),
    (72, 40, 32),
    (12, 4, 8),
])
def test_bank_transaction(zero_bank_account, num1, num2, expected):
    zero_bank_account.deposit(num1)
    zero_bank_account.withdraw(num2)
    assert zero_bank_account.balance == expected
```

### Example 3 — Testing invalid login credentials:
```python
@pytest.mark.parametrize("email, password, status_code", [
    ('wrongemail@gmail.com', 'password123', 403),
    ('sanjeev@gmail.com', 'wrongpassword', 403),
    ('wrongemail@gmail.com', 'wrongpassword', 403),
    (None, 'password123', 422),
    ('sanjeev@gmail.com', None, 422)
])
def test_incorrect_login(test_user, client, email, password, status_code):
    res = client.post("/login", data={"username": email, "password": password})
    assert res.status_code == status_code
```

**What I know:**
- Each tuple in the list becomes a **separate test case**.
- Parametrize can be combined with fixtures (e.g., `zero_bank_account`, `test_user`).
- Great for testing **boundary conditions** and **error cases** without duplicating test functions.
- The parameter names in the decorator string must match the function arguments.

---

## 8. Exception Testing (`pytest.raises`)

```python
def test_insufficient_funds(bank_account):
    with pytest.raises(InsufficientFunds):
        bank_account.withdraw(200)
```

**What I know:**
- `pytest.raises(ExceptionType)` is a **context manager** that asserts the code inside raises that specific exception.
- If the exception is NOT raised, the test **fails**.
- I use this to verify that my `BankAccount.withdraw()` properly raises `InsufficientFunds` when balance is too low.

---

## 9. Schema Validation in Tests

I validate API responses against my **Pydantic schemas**:

```python
new_user = schemas.UserOut(**res.json())    # validates user response shape
created_post = schemas.Post(**res.json())   # validates post response shape
login_res = schemas.Token(**res.json())     # validates token response shape
post = schemas.PostOut(**res.json())        # validates post-with-votes shape
```

**What I know:**
- Unpacking (`**res.json()`) into a Pydantic model acts as **response contract validation**.
- If the API response is missing a required field or has the wrong type, Pydantic raises a `ValidationError` and the test fails.
- This catches regressions where the API response shape accidentally changes.

---

## 10. JWT Token Verification in Tests

```python
def test_login_user(client, test_user):
    res = client.post("/login", data={"username": test_user['email'], "password": test_user['password']})
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token, settings.secret_key, algorithms=[settings.algorithm])
    id = payload.get("user_id")
    assert id == test_user['id']
    assert login_res.token_type == "bearer"
```

**What I know:**
- I can **decode the JWT** in the test to verify the payload contains the correct `user_id`.
- I use `python-jose` (`from jose import jwt`) for decoding.
- The `secret_key` and `algorithm` come from the same `settings` the app uses — ensures consistency.

---

## 11. Authorization Testing Patterns

I test **four authorization scenarios** consistently across resources:

| Scenario | Expected Status | Example Test |
|---|---|---|
| Authorized user, valid request | `200` / `201` / `204` | `test_get_all_posts`, `test_create_post`, `test_delete_post_success` |
| Unauthorized user (no token) | `401` | `test_unauthorized_user_get_all_posts`, `test_unauthorized_user_create_post` |
| Authorized user, resource not found | `404` | `test_get_one_post_not_exist`, `test_delete_post_non_exist` |
| Authorized user, not the owner | `403` | `test_delete_other_user_post`, `test_update_other_user_post` |

**What I know:**
- I use `client` (no auth) vs `authorized_client` (with auth) to test the 401 vs 200 split.
- I use `test_posts[3]` (owned by `test_user2`) to test the 403 ownership boundary.
- I use non-existent IDs (like `88888`, `8000000000`) to test 404 handling.

---

## 12. CRUD Test Coverage

For the **Posts** resource, I test the full CRUD lifecycle:

| Operation | Happy Path | Unauthorized | Not Found | Not Owner |
|---|---|---|---|---|
| **C**reate | `test_create_post` (parametrized), `test_create_post_default_published_true` | `test_unauthorized_user_create_post` | — | — |
| **R**ead (all) | `test_get_all_posts` | `test_unauthorized_user_get_all_posts` | — | — |
| **R**ead (one) | `test_get_one_post` | `test_unauthorized_user_get_all_posts` (2nd one) | `test_get_one_post_not_exist` | — |
| **U**pdate | `test_update_post` | `test_unauthorized_user_update_post` | `test_update_post_non_exist` | `test_update_other_user_post` |
| **D**elete | `test_delete_post_success` | `test_unauthorized_user_delete_post` | `test_delete_post_non_exist` | `test_delete_other_user_post` |

---

## 13. Unit Tests vs Integration Tests

I've written **both types**:

### Unit Tests (`test_calculations.py`)
- Test pure Python functions and classes **in isolation**.
- No database, no HTTP, no FastAPI.
- Fast and deterministic.
- Examples: `test_add`, `test_subtract`, `test_withdraw`, `test_insufficient_funds`.

### Integration Tests (`test_users.py`, `test_posts.py`, `test_votes.py`)
- Test full API endpoints **through the HTTP layer**.
- Involve database reads/writes, authentication, and response validation.
- Slower but test the full stack (router → business logic → DB → response).

---

## 14. Testing Patterns & Techniques Summary

| Technique | Where I Used It |
|---|---|
| `@pytest.fixture` | `conftest.py` — session, client, users, auth, seed data |
| `@pytest.mark.parametrize` | `test_calculations.py`, `test_users.py`, `test_posts.py` |
| `pytest.raises()` | `test_calculations.py` — exception testing |
| `yield` fixtures (setup/teardown) | `session`, `client` |
| Fixture chaining | `client` → `test_user` → `token` → `authorized_client` |
| Dependency override | `app.dependency_overrides[get_db]` in `client` fixture |
| Pydantic schema validation | `test_users.py`, `test_posts.py` |
| JWT decode verification | `test_users.py` |
| Separate test database | `conftest.py` — `test_{database_name}` |
| Form data vs JSON | `data={}` for login, `json={}` for everything else |
| Direct ORM seeding | `test_posts`, `test_votes` fixtures |

---

## 15. Things I Explored But Moved Away From

Based on commented-out code:

- **Alembic for test migrations** — I explored using `command.upgrade("head")` and `command.downgrade("base")` but settled on `Base.metadata.create_all/drop_all` for simplicity.
- **Separate `database.py` test file** — I originally had DB setup in a separate `test/database.py` but consolidated everything into `conftest.py`.
- **Inline fixture definitions** — `test_user` was originally defined inside `test_users.py` before moving it to `conftest.py` for reuse.
- **Hardcoded DB URLs** — I moved from `postgresql://postgres:dhisdat@localhost:5432/test_fastapi` to environment-variable-driven URLs via `settings`.

---

## 16. Key Assertions I Use

```python
assert res.status_code == 201          # HTTP status check
assert new_user.email == "..."         # field value check
assert created_post.owner_id == ...    # ownership check
assert login_res.token_type == "bearer" # token format check
assert round(bank_account.balance) == 55  # floating-point rounding
assert post.Post.id == test_posts[0].id   # nested model check
```

---

> **Total test count: ~33 tests** covering unit logic, authentication, CRUD operations, authorization boundaries, and voting functionality.
