# "Database code" for the DB News.

import psycopg2

DBNAME = "news"


def get_most_popular_three_articles():
    """Return most popluar three articles
    from the 'database', most recent first."""
    db, crusor = connect()
    query = """
      SELECT title, count(log.path) as sum
      FROM articles
      JOIN log ON log.path = concat('/article/',articles.slug)
      GROUP BY title
      ORDER BY sum desc limit 3
      """
    crusor.execute(query)
    result = crusor.fetchall()
    output = '  "%s" -- %s views\n'
    top_articles = "".join(output % (title, str(sum)) for title, sum in result)
    print('\n1. What are the most popular three articles of all time?')
    print(top_articles)
    db.close()
    return result


def get_most_popular_author():
    """Return most popluar article author of all time from the 'database' """
    db, crusor = connect()
    query = """
      SELECT authors.name AS author, count(log.path) AS views
      FROM articles, authors, log
      WHERE authors.id = articles.author
        AND log.path = concat('/article/', articles.slug)
      GROUP BY authors.name
      ORDER BY views desc
      """
    crusor.execute(query)
    result = crusor.fetchall()
    output = '  "%s" -- %s views\n'
    top_authors = "".join(output % (author, views) for author, views in result)
    print('\n2. Who are the most popular article authors of all time?')
    print(top_authors)
    db.close()
    return result


def get_date_when_error_test_failed():
    """Return days where more than 1% of requests lead to errors
    from the 'database' """
    db, crusor = connect()
    query = """
        SELECT
            to_char(errorTest.date, 'Mon DD, YYYY'),
            ROUND(errorTest.percentage_error, 2)
        FROM (
            SELECT status_error.date AS date,
                CAST((SUM(status_error.errors))/(SUM(status_total.total)) * 100
                AS numeric) AS percentage_error
            FROM (SELECT
                      date(time) AS date,
                      count(status) AS errors
                  FROM log
                  WHERE status
                  LIKE '404%'
                  GROUP BY date) AS status_error
            JOIN (SELECT
                      date(time) AS date,
                      count(status) AS total
                  FROM log
                  GROUP BY date) AS status_total
            ON status_error.date = status_total.date
            GROUP BY status_error.date
        ) AS errorTest
        WHERE errorTest.percentage_error > 1.0
    """
    crusor.execute(query)
    result = crusor.fetchall()
    output = '  %s -- %s'
    error_test = "".join(
        output % (str(date), str(error)) for date, error in result
    )
    print('\n 3. On which days did more than 1 percentage of requests'
          + ' lead to errors?'
          )
    print(error_test + ' %' + 'errors\n')
    db.close()
    return result


# SUGGESTION : Since these lines are repeating in different functions,
# its better to implement a function and reuse that.
def connect(database_name="news"):
    try:
        db = psycopg2.connect("dbname={}".format(database_name))
        cursor = db.cursor()
        return db, cursor
    except psycopg2.DatabaseError, e:
        print("\nDB connection failed. Error Message is :")
        print(e)
