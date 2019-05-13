from rest_framework import status
from .basetests import HighlightBaseTests


class TestArticles(HighlightBaseTests):
    """
    Class to test highlighting
    """
    text = "purpose"
    field = "body"
    message = "Highlight removed"
    updated_comment = "A new one"
    detail = "You cannot delete or update highlight that is not yours"
    not_found = "Highlight removed or does not exist"
    not_supported = "Field must be; title, body or description"
    start_error = "Start index cannot be greater than End index"
    range_error = "start or end index cannot be greater than field length"
    field_error = "You cannot update the field"
    index_error = "Start index or end index cannot be a negative number"

    def test_successful_highlight_creation(self):
        """
        Test successful creation of a highlight
        """
        response = self.create_highlight()
        res = response.data.get("highlight").get("highlighted_text")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res, self.text)

    def test_successful_title_highlight(self):
        """
        Test successful title highlight
        """
        response = self.create_title_highlight()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_successful_description_highlight(self):
        """
        Test successful description highlight
        """
        response = self.create_description_highlight()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_all_article_highlights_by_user(self):
        """
        Test successful get all article highlights by a user
        """
        response = self.get_all_highlights()
        res = response.data.get("highlights")[0].get("field")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(res, self.field)

    def test_remove_highlight_by_user(self):
        """
        Test successful remove a highlight by a user
        """
        response = self.remove_one_highlight()
        res = response.data["message"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(res, self.message)

    def test_update_highlight_by_user(self):
        """
        Test successful update highlight by a user
        """
        response = self.update_one_highlight()
        res = response.data.get("highlight").get("comment")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(res, self.updated_comment)

    def test_update_not_permitted(self):
        """
        Test update highlight not permitted
        """
        response = self.update_not_permitted()
        res = response.data["detail"]
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res, self.detail)

    def test_delete_not_permitted(self):
        """
        Test delete highlight not permitted
        """
        response = self.delete_not_permitted()
        res = response.data["detail"]
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res, self.detail)

    def test_highlight_not_found(self):
        """
        Test highlight not found
        """
        response = self.highlight_not_found()
        res = response.data["detail"]
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(res, self.not_found)

    def test_field_not_supported(self):
        """
        Test field not supported
        """
        response = self.field_not_supported()
        res = response.data["detail"]
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(res, self.not_supported)

    def test_wrong_start_index(self):
        """
        Test Start index greater than End index
        """
        response = self.start_index_wrong()
        res = response.data["detail"]
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res, self.start_error)

    def test_index_out_of_range(self):
        """
        Test Index greater than length of string
        """
        response = self.index_out_of_range()
        res = response.data["detail"]
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res, self.range_error)

    def test_update_field_error(self):
        """
        Test update field error
        """
        response = self.update_field_error()
        res = response.data["detail"]
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res, self.field_error)

    def test_negative_index(self):
        """
        Test negative index
        """
        response = self.index_negative()
        res = response.data["detail"]
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res, self.index_error)

    def test_update_negative_index(self):
        """
        Test update negative index
        """
        response = self.update_negative_index()
        res = response.data["detail"]
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res, self.index_error)

    def test_update_out_of_range_index(self):
        """
        Test update out of range index
        """
        response = self.update_out_of_range()
        res = response.data["detail"]
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res, self.range_error)
