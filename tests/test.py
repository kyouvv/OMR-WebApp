from run import PaperFinder

paperfinder = PaperFinder()

paperfinder.path = 'static/results'

paperfinder.findpaper('paper_test1.png', [(1, 'a')])