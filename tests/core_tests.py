from mock import patch
import pyseries


@patch('pyseries.download')
def test_main_function(download_mock):
    download_mock.return_value = True
    pyseries.main('tests/examples/')
