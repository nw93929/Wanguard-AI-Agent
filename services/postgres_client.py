from psycopg2 import pool, sql
import os
from typing import List, Tuple, Optional, Any
from contextlib import contextmanager

'''
Secure Postgres database client with connection pooling and parameterized queries.
Prevents SQL injection and manages connections efficiently.
'''

# Initialize connection pool (singleton pattern)
_connection_pool = None

def get_connection_pool():
    """Creates or returns existing connection pool"""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=os.getenv("POSTGRES_URI")
        )
    return _connection_pool

@contextmanager
def get_db_connection():
    """Context manager for database connections from pool"""
    conn_pool = get_connection_pool()
    conn = conn_pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn_pool.putconn(conn)

def query_internal_db(
    query: str,
    params: Optional[Tuple[Any, ...]] = None,
    fetch_one: bool = False
) -> str:
    """
    Execute a parameterized SQL query safely.

    Args:
        query: SQL query with %s placeholders for parameters
        params: Tuple of parameters to safely inject into query
        fetch_one: If True, returns only first row; otherwise returns all rows

    Returns:
        String representation of query results

    Example:
        # Safe parameterized query
        results = query_internal_db(
            "SELECT * FROM stocks WHERE ticker = %s AND price > %s",
            ("AAPL", 150.0)
        )
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)

            if fetch_one:
                result = cur.fetchone()
            else:
                result = cur.fetchall()

            return f"Database Results: {str(result)}"

def query_stock_financials(
    ticker: str,
    metric_names: Optional[List[str]] = None,
    start_date: Optional[str] = None
) -> List[Tuple]:
    """
    Safe helper function to query stock financial metrics.

    Args:
        ticker: Stock ticker symbol
        metric_names: List of metric names to filter (e.g., ['revenue', 'net_income'])
        start_date: Filter for dates >= this value (format: 'YYYY-MM-DD')

    Returns:
        List of tuples containing query results
    """
    base_query = "SELECT * FROM financials WHERE ticker = %s"
    params = [ticker]

    if metric_names:
        placeholders = ', '.join(['%s'] * len(metric_names))
        base_query += f" AND metric_name IN ({placeholders})"
        params.extend(metric_names)

    if start_date:
        base_query += " AND report_date >= %s"
        params.append(start_date)

    base_query += " ORDER BY report_date DESC"

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(base_query, tuple(params))
            return cur.fetchall()

def execute_safe_query(
    table_name: str,
    columns: List[str] = None,
    where_conditions: dict = None,
    order_by: str = None,
    limit: int = None
) -> List[Tuple]:
    """
    Build and execute a safe SELECT query using sql.Identifier for table/column names.

    Args:
        table_name: Name of the table to query
        columns: List of column names to select (None = SELECT *)
        where_conditions: Dict of {column: value} for WHERE clause
        order_by: Column name to order by
        limit: Maximum number of rows to return

    Returns:
        List of tuples containing query results
    """
    # Build SELECT clause
    if columns:
        select_clause = sql.SQL(", ").join([sql.Identifier(col) for col in columns])
    else:
        select_clause = sql.SQL("*")

    query = sql.SQL("SELECT {} FROM {}").format(
        select_clause,
        sql.Identifier(table_name)
    )

    params = []

    # Build WHERE clause
    if where_conditions:
        where_parts = []
        for col, val in where_conditions.items():
            where_parts.append(sql.SQL("{} = %s").format(sql.Identifier(col)))
            params.append(val)

        query = sql.SQL("{} WHERE {}").format(
            query,
            sql.SQL(" AND ").join(where_parts)
        )

    # Add ORDER BY
    if order_by:
        query = sql.SQL("{} ORDER BY {}").format(
            query,
            sql.Identifier(order_by)
        )

    # Add LIMIT
    if limit:
        query = sql.SQL("{} LIMIT %s").format(query)
        params.append(limit)

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, tuple(params))
            return cur.fetchall()