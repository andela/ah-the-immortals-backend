from rest_framework.renderers import JSONRenderer
import json


class ArticleJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        if isinstance(data, dict):
            errors = data.get('errors', None)
            if errors is not None:
                return super(ArticleJSONRenderer, self).render(data)
        if data is not None:
            return json.dumps({
                'article': data
            })
