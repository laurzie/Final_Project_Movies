from Proj4 import *
import unittest

class TestMovie(unittest.TestCase):
    def test_basic_search(self):
        results = get_results_for_movie("love")
        movie_objects,list_of_movie, list_of_ids = results
        self.assertEqual(len(results), 3)
        self.assertEqual(len(list_of_movie), 120)
        self.assertEqual(len(list_of_ids), 120)
        self.assertEqual(movie_objects[0].movie_id, 54320)
        self.assertEqual(movie_objects[11].release_date, str(2009))


class TestMovieSpecificInfo(unittest.TestCase):
    def test_details_search(self):
        results = get_info_for_movie("love")
        self.assertEqual(len(results), 120)
        self.assertEqual(results[3][3], "Comedy")
        self.assertEqual(results[3][4], None)
        self.assertEqual(results[3][5], None)

class TestDatabase(unittest.TestCase):

    def test_List_of_Movies_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT Id FROM List_of_Movies'
        results = cur.execute(sql)
        result_list = results.fetchall()
        # self.assertIn(result_list[0],508)
        self.assertEqual(len(result_list), 120)

    def test_Movies_Info_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT Movie_Id FROM Movie_Info'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list), 120)

    def test_joins(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        sql = '''
            SELECT Popularity_score, Vote_average
            FROM List_of_Movies
            JOIN Movie_Info
            ON List_of_Movies.Id = Movie_Info.Movie_Id
            WHERE Genre_1 = "Comedy" and Genre_2 = "Romance" or  Genre_1 = "Comedy" and Genre_2 = "Romance"
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list), 12)
        self.assertEqual(result_list[2][1], 4.2)

        conn.close()


    def test_joins(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        sql = '''
            SELECT Runtime, Genre_1
            FROM List_of_Movies
            JOIN Movie_Info
            ON List_of_Movies.Id = Movie_Info.Movie_Id
            GROUP BY Genre_1
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list), 14)
        self.assertEqual(result_list[3][0], 105)

        conn.close()


if __name__ == '__main__':
    unittest.main()
