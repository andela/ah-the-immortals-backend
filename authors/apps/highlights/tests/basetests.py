from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework.reverse import reverse
from rest_framework.authtoken.models import Token
import json
from authors.apps.highlights.models import Highlight
from authors.apps.articles.tests.basetests import BaseTest

User = get_user_model()


class HighlightBaseTests(BaseTest):
    """
    Class to set up test case
    """
    highlight_url = reverse("highlights:highlight", args=["this-is-mine"])
    new_highlight = {
            "field": "body",
            "comment": "This is awesome",
            "start_index": 12,
            "end_index": 18
        }
    test_title = {
            "field": "title",
            "comment": "This is awesome",
            "start_index": 0,
            "end_index": 3
        }
    test_description = {
            "field": "description",
            "comment": "This is awesome",
            "start_index": 5,
            "end_index": 7
        }
    wrong_field = {
            "field": "name",
            "comment": "This is awesome",
            "start_index": 12,
            "end_index": 18
        }
    wrong_start = {
            "field": "body",
            "comment": "This is awesome",
            "start_index": 22,
            "end_index": 18
        }
    out_of_range = {
            "field": "body",
            "comment": "This is awesome",
            "start_index": 12,
            "end_index": 100
        }
    update_highlight = {
            "comment": "A new one"
        }
    update_field = {
            "field": "description"
        }
    negative_index = {
            "field": "body",
            "comment": "This is awesome",
            "start_index": -2,
            "end_index": 18
        }
    negative_start = {
            "start_index": -2,
        }
    greater_end = {
            "end_index": 1000,
        }

    def create_highlight(self):
        """
        Create a new highlight
        """
        self.create_article()
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        return self.client.post(self.highlight_url,
                                data=json.dumps(self.new_highlight),
                                content_type="application/json")

    def create_title_highlight(self):
        """
        Highlight title
        """
        self.create_article()
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        return self.client.post(self.highlight_url,
                                data=json.dumps(self.test_title),
                                content_type="application/json")

    def create_description_highlight(self):
        """
        Highlight description
        """
        self.create_article()
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        return self.client.post(self.highlight_url,
                                data=json.dumps(self.test_description),
                                content_type="application/json")

    def get_all_highlights(self):
        """
        Return all highlights
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        self.create_highlight()
        return self.client.get(self.highlight_url)

    def remove_one_highlight(self):
        """
        Remove one highlight
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        highlight = self.create_highlight()
        id = highlight.data.get("highlight").get("id")
        return self.client.delete(reverse("highlights:highlights",
                                          args=["this-is-mine", id]))

    def update_one_highlight(self):
        """
        Update one highlight
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        highlight = self.create_highlight()
        id = highlight.data.get("highlight").get("id")
        return self.client.patch(reverse("highlights:highlights",
                                         args=["this-is-mine", id]),
                                 data=json.dumps(self.update_highlight),
                                 content_type="application/json")

    def update_not_permitted(self):
        """
        Update not permitted
        """
        highlight = self.create_highlight()
        id = highlight.data.get("highlight").get("id")
        self.is_authenticated("jim@gmail.com", "@Us3r.com")
        return self.client.patch(reverse("highlights:highlights",
                                         args=["this-is-mine", id]),
                                 data=json.dumps(self.update_highlight),
                                 content_type="application/json")

    def delete_not_permitted(self):
        """
        Delete not permitted
        """
        highlight = self.create_highlight()
        id = highlight.data.get("highlight").get("id")
        self.is_authenticated("jim@gmail.com", "@Us3r.com")
        return self.client.delete(reverse("highlights:highlights",
                                          args=["this-is-mine", id]))

    def highlight_not_found(self):
        """
        Highlight not found
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        self.create_highlight()
        return self.client.delete(reverse("highlights:highlights",
                                          args=["this-is-mine", 10]))

    def field_not_supported(self):
        """
        Field not supported
        """
        self.create_article()
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        return self.client.post(self.highlight_url,
                                data=json.dumps(self.wrong_field),
                                content_type="application/json")

    def start_index_wrong(self):
        """
        Start index greater than End index
        """
        self.create_article()
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        return self.client.post(self.highlight_url,
                                data=json.dumps(self.wrong_start),
                                content_type="application/json")

    def index_out_of_range(self):
        """
        Index greater than length of string
        """
        self.create_article()
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        return self.client.post(self.highlight_url,
                                data=json.dumps(self.out_of_range),
                                content_type="application/json")

    def update_field_error(self):
        """
        Update field error
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        highlight = self.create_highlight()
        id = highlight.data.get("highlight").get("id")
        return self.client.patch(reverse("highlights:highlights",
                                         args=["this-is-mine", id]),
                                 data=json.dumps(self.update_field),
                                 content_type="application/json")

    def index_negative(self):
        """
        Negative index
        """
        self.create_article()
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        return self.client.post(self.highlight_url,
                                data=json.dumps(self.negative_index),
                                content_type="application/json")

    def update_negative_index(self):
        """
        Update negative index
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        highlight = self.create_highlight()
        id = highlight.data.get("highlight").get("id")
        return self.client.patch(reverse("highlights:highlights",
                                         args=["this-is-mine", id]),
                                 data=json.dumps(self.negative_start),
                                 content_type="application/json")

    def update_out_of_range(self):
        """
        Update index out of range
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        highlight = self.create_highlight()
        id = highlight.data.get("highlight").get("id")
        return self.client.patch(reverse("highlights:highlights",
                                         args=["this-is-mine", id]),
                                 data=json.dumps(self.greater_end),
                                 content_type="application/json")
