---
id: sql
title: SQL
enabled: true
blocking: true
order: 70
category: code-quality
keywords: [sqlalchemy, embedded sql, f-string sql, orm, ddl, migration, raw sql]
description: Use when code touches database queries, raw SQL, migrations, DDL, binds, SQLAlchemy, ORM, or SQL resources.
---

# SQL

## Core rule

Use SQLAlchemy ORM or the project DB layer for application queries. Raw SQL belongs in package resources or migration scripts, never embedded in business modules.

Whenever possible, use the HeavenBase-provided `Database` class instead of the raw SQLAlchemy engine.

## Apply when

- Code executes database queries, migrations, DDL, or raw SQL.
- Code introduces SQL resources or query helper APIs.
- Code touches SQLAlchemy engines/sessions or HeavenBase database wrappers.

## Do

- Use ORM/project DB APIs for application queries.
- Parameterize binds through project helpers.
- Keep static raw SQL under resources.
- Put schema migrations in scripts or the migration system.

## Avoid

- f-string SQL, string interpolation, or concatenation.
- Ad-hoc DDL in handlers.
- Raw SQLAlchemy engine access when the project DB layer supports the operation.

## Example

```python
def load_user(db, user_id: str):
    return db.execute(f"select * from users where id = '{user_id}'")
```

```python
def load_user(db: Database, user_id: str) -> User:
    stmt = select(User).where(User.id == user_id)
    return db.execute(stmt).scalar_one()
```

## Raw SQL exception

```python
sql = load_txt(CM_HVNB.pj("&", "sql", "refresh_catalog.sql"))
db.execute(sql, {"target_id": target_id})
```

Raw SQL must be static, resource-backed, and parameterized.

## Related rules

Also apply [config.md](config.md) for SQL resources and database defaults, [util.md](util.md) for resource loading, and [types.md](types.md) for query result contracts.
