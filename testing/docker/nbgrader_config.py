from nbgrader.exchange import ngshare

c = get_config()

# Use the ngshare exchange plugin.
c.ExchangeFactory.exchange = ngshare.Exchange
c.ExchangeFactory.fetch_assignment = ngshare.ExchangeFetchAssignment
c.ExchangeFactory.fetch_feedback = ngshare.ExchangeFetchFeedback
c.ExchangeFactory.release_assignment = ngshare.ExchangeReleaseAssignment
c.ExchangeFactory.release_feedback = ngshare.ExchangeReleaseFeedback
c.ExchangeFactory.list = ngshare.ExchangeList
c.ExchangeFactory.submit = ngshare.ExchangeSubmit
c.ExchangeFactory.collect = ngshare.ExchangeCollect

c.NbGrader.logfile = '/tmp/nbgrader.log'
