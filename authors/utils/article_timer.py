class ArticleTimer:
    """
    Read timer class for articles
    """

    def __init__(self, article):
        self.article = article
        self.words_per_minute = 265

    def get_title(self):
        """
        Get title of article
        """
        return self.article.title

    def get_body(self):
        """
        Gets body of the article
        """
        return self.article.body

    def get_description(self):
        """
        Gets description of the article
        """
        return self.article.description

    def get_tags(self):
        """
        Gets all words on a tag
        """
        tag_words = []
        [tag_words.extend(tagword.split()) for tagword in self.article.tagList]
        return tag_words

    def get_article_info(self):
        """
        Gets the whole informnation of an article
        """
        info = []
        info.extend(self.get_title().split())
        info.extend(self.get_body().split())
        info.extend(self.get_description().split())
        info.extend(self.get_tags())
        return info

    def get_read_time(self):
        """
        Gets the read time of the article
        """
        word_length = len(self.get_article_info())
        read_time = 0
        if word_length:
            timer = word_length/self.words_per_minute
        if timer < 1:
            read_time = str(round(timer*60))+" seconds"
        else:
            read_time = str(round(timer))+" minutes"
        return read_time
