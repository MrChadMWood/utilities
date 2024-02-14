def exec(q, db_params=None, conn=None, is_dataset=False):
    """
    Execute the given SQL query and return the result.

    Parameters:
    q : str
        The SQL query to be executed.
    db_params : dict, optional
        Dictionary containing parameters for establishing a database connection
        (default is None).
    conn : psycopg2.extensions.connection, optional
        Existing database connection object (default is None). If not provided,
        a new connection will be established using `db_params`.
    is_dataset : bool, optional
        Indicates whether the query returns a dataset (default is False). If True,
        the result will be a list of dictionaries where each dictionary represents
        a row of data with keys corresponding to the column names. If False, the result
        will be the return value of the `cursor.execute` method.

    Returns:
    list of dict or any : The result of the query execution.
        If `is_dataset` is True, returns a list of dictionaries where each dictionary
        represents a row of data with keys corresponding to the column names. If `is_dataset`
        is False, returns the return value of the `cursor.execute` method.

    Raises:
    Exception: If any error occurs during query execution, an exception is raised.
    """
    response = None
    try:
        # Establishes connection
        if conn is None:
            conn = psycopg2.connect(**db_params)

        # Collects response
        with conn.cursor() as cursor:
            response = cursor.execute(q)
            if is_dataset:
                data = []
                headers = [desc[0] for desc in cursor.description]
                for row in cursor.fetchall():
                    data.append(dict(zip(headers, row)))
                return data
            else:
                conn.commit()
                return response
        
    except Exception as e:
        if conn is not None:
            conn.rollback()
            conn.close()
        raise Exception from e
