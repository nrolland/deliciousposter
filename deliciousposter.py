#!/usr/bin/env python -c
import sys, getopt
from functools import reduce, partial
maximum = partial(reduce, max)


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "htc", ["help", "test", "confirm"])
        except getopt.error, msg:
             raise Usage(msg)
        
        test = False;
        confirmit=False
        for o, a in opts:
            if o in ("-h", "--help"):
                raise Usage(__file__ +' [--test -t] [--confirm -c] delicious_login wordpress_xmlrpc_endpoint wp_login wp_password [delicious_tag] [weekly_posts_title] ')
            if o in ("-t", "--test"):
                print >>sys.stdout, 'TEST MODE'
                test = True
            if o in ("-c", "--confirm"):
                confirmit = True
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
        recentposts = blog.get_recent_posts()
        recentposts = [post for post in recentposts 
                        if string.find(post['title'], weeklypost_title) > -1]
        lastpub = maximum([post['date_created_gmt'] for post in recentposts],
                           datetime.datetime(1900, 01, 01))
        
        if(lastpub == datetime.datetime(1900, 01, 01)):
          if str(raw_input("No previous posts with tag " +weeklypost_title +" has been found do you want to continue ? Type y,n\n")) != "y":
              print "canceling upload"
              return
        
        html = "<div><dl>"
        nb=0
        #print user_metadata.bookmarks
        titles = []
        for post in user_metadata.bookmarks:
            if any(tag == delicious_tag for tag in post[itags]) and post[idate] > lastpub:
                html +=  "<dt>" + "<a href=\"" + post[iurl] + "\">" 
                titles.append(len(post[ititle])>0 and post[ititle] or (len(post[icomment]) < 100 and post[icomment] or "link"))
                html +=  titles[-1]
                html +=  "</a></dt>"
                html += "<dd>" +  post[icomment] + "</dd>"
                nb = nb + 1
        html = html + "</dl></div>"
        
        if nb>0:
            newpost = { 'title': weeklypost_title +" for " + datetime.date.today().strftime("%y/%m/%d"),'description': html }
            if test:
                print >>sys.stdout, newpost
            else:                
                if confirmit:
                    print titles
                    if str(raw_input("Want to publsih this ? Type y,n\n")) != "y":
                        print "canceling upload"
                        return
                blog.new_post(newpost)
        else:
            if confirmit:
                print "There was nothing to be sent and confirm"
        
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2


if __name__ == "__main__":
    sys.exit(main())