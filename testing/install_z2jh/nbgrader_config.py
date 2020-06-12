from ngshare_exchange import configureExchange

c = get_config()
configureExchange(
    c, 'http://ngshare.default.svc.cluster.local:8080/services/ngshare'
)

# Add the following to let students access courses without configuration
# For more information, read Notes for Instructors in the documentation
c.CourseDirectory.course_id = '*'
