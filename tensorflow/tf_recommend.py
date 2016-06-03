#!/usr/bin/python

#roman@dotmodus.com
# ---
# nlp and prediction/recommendation tools for text article based data using google tools
# ---

def main():
    #get data from BQ
    sProjectID = 'scoop-24-dev'
    sDatasetID = 'articles'
    sTableID = 'archive_short'
    sQuery = "SELECT * FROM {}.{}".format(sDatasetID, sTableID)

    from pandas.io import gbq
    dfAllArticles = gbq.read_gbq(sQuery, sProjectID)

    aHeadings = dfAllArticles.columns.values



    aArticle = dfAllArticles.values[0]

    oArticle = Article(aHeadings, aArticle)










class Article:

    def __init__(self, aHeadings, aOrigArticle):
        """class that describes all different aspects of an article"""
        self.aOrigArticle = aOrigArticle
        self.aHeadings = aHeadings

    #plain text
    #markup
    #POS
    #specials

    #subject
    #keywords
    #summary
    #category








#recommend
    #recommend content to users
    #recommend users to content











if __name__ == '__main__':
    main()
