from nbgrader.auth import JupyterHubAuthPlugin
from nbgrader.exchange import ngshare

c = get_config()

# Select which exchange service to use.
try:
    if True:
        c.ExchangeFactory.exchange = ngshare.Exchange
        c.ExchangeFactory.fetch_assignment = ngshare.ExchangeFetchAssignment
        c.ExchangeFactory.fetch_feedback = ngshare.ExchangeFetchFeedback
        c.ExchangeFactory.release_assignment = ngshare.ExchangeReleaseAssignment
        c.ExchangeFactory.release_feedback = ngshare.ExchangeReleaseFeedback
        c.ExchangeFactory.list = ngshare.ExchangeList
        c.ExchangeFactory.submit = ngshare.ExchangeSubmit
        c.ExchangeFactory.collect = ngshare.ExchangeCollect
except e:
    print("Failed to set exchange service.")
    print(e)

c.NbGrader.logfile = '/tmp/nbgrader.log'
