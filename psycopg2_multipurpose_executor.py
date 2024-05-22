import psycopg2


# Postgres query handler
def psql_exec(q, db_params=None, conn=None, return_data=False, q_params: tuple = ()):
    """
    Execute the given SQL query and return the result.

    Parameters:
    q : str
        The SQL query to be executed.
    db_params : dict, optional
        Dictionary containing parameters for establishing a database connection.
        Must include keys such as 'dbname', 'user', 'password', and 'host'.
        Default is None.
    conn : psycopg2.extensions.connection, optional
        Existing database connection object. If not provided, a new connection
        will be established using `db_params`. Default is None.
    return_data : bool, optional
        Indicates whether the query returns a dataset. Default is False.
        If True, the result will be a list of dictionaries where each dictionary
        represents a row of data with keys corresponding to the column names.
        If False, the result will be the return value of the `cursor.execute` method.
    q_params : tuple, optional
        Parameters to be used in the SQL query. Default is an empty tuple.

    Returns:
    list of dict or any : The result of the query execution.
        If `return_data` is True, returns a list of dictionaries where each dictionary
        represents a row of data with keys corresponding to the column names.
        If `return_data` is False, returns the return value of the `cursor.execute` method.

    Raises:
    ValueError: If neither `db_params` nor `conn` is provided.
    Exception: If any error occurs during query execution, an exception is raised.
    """
    close_conn = False
    if not db_params and not conn:
        raise ValueError('Either `db_params` or `conn` is required.')
        
    try:
        # Establishes connection
        if conn is None:
            close_conn = True
            conn = psycopg2.connect(**db_params)

        # Collects response
        with conn.cursor() as cursor:
            cursor.execute(q, q_params)
            if return_data:
                data = []
                headers = [desc[0] for desc in cursor.description]
                for row in cursor.fetchall():
                    data.append(dict(zip(headers, row)))
            else:
                data = conn.commit()
                
    except Exception as e:
        if conn is not None:
            conn.rollback()
            if close_conn:
                conn.close()
        raise e   
        
    else:
        if close_conn:
            conn.close()
        return data
