import sys, getopt

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "ht", ["help"])
        except getopt.error, msg:
             raise Usage(msg)
        
        test = False;
        for o, a in opts:
            if o in ("-h", "--help"):
                raise Usage(__file__ +' [--test -t] delicious_login wordpress_xmlrpc_endpoint wp_login wp_password [delicious_tag] [weekly_posts_title] ')
            if o in ("-t", "--test"):
                print >>sys.stdout, 'TEST MODE'
                test = True
        if len(args)<4 :
            raise Usage("arguments missing")        
        
        iurl = 0
        itags =1
        ititle = 2
        icomment = 3
        idate = 4
        
        import string
        import pyblog
        import deliciousapi
        
        
        deliciouslogin=args[0]
        wpurl=args[1]
        wplogin =args[2]
        wppassword =args[3]
        
        delicious_tag = len(args)>4 and args[4] or 'weekly_links'
        weeklypost_title = len(args)>5 and args[5] or 'Weekly links'

        
        
        blog = pyblog.WordPress(wpurl, wplogin, wppassword)
        dapi = deliciousapi.DeliciousAPI()
        user_metadata = dapi.get_user(deliciouslogin)
        
        import datetime
        lastpub = datetime.datetime.min
        recentposts = blog.get_recent_posts()
        for post in recentposts:
            if string.find(post['title'], weeklypost_title) > -1:
                lastpub = post['date_created_gmt']
        
        
        html = "<div><dl>"
        nb=0
        #print user_metadata.bookmarks
        for post in user_metadata.bookmarks:
            if any(tag == delicious_tag for tag in post[itags]) and post[idate] > lastpub:
                #print post
                html = html + "<dt>" + "<a href=" + post[iurl] + ">" + (len(post[ititle])>0 and post[ititle] or (len(post[icomment]) < 100 and post[icomment] or "link"))   + "</a>"
                html = html + "<dd>" +  post[icomment]
                nb = nb + 1
        html = html + "</dl></div>"
        
        if nb>0:
            newpost = { 'title': weeklypost_title +" for " + datetime.date.today().strftime("%y/%m/%d"),'description': html }
            if test:
                print >>sys.stdout, newpost
            else:
                blog.new_post(newpost)
    
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2


if __name__ == "__main__":
    sys.exit(main())