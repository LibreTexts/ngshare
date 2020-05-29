from ngshare_exchange import configureExchange
c=get_config()
configureExchange(c)
c.CourseDirectory.course_id = '*'
