
# ABIPPITY & SAPINESS

I got interested in [SAP SE](https://en.wikipedia.org/wiki/SAP_SE)
at some point, and wanted to play with it on my laptop.
But it's... really not designed for that.
So I looked for an emulator, but found none.

Therefore, I decided to write a SAP emulator in Python.
Things quickly got out of hand.

I'm particularly proud of the [lexer](/abippity/abippity/lex.py)
and [parser](/abippity/abippity/parse.py), which are incredibly compact,
with the majority of the language's grammar actually specified by a text file:
[syntax.txt](/abippity/abippity/syntax.txt)
That text file is largely copy-paste-edited from the excellent
[help.sap.com ABAP Documentation](https://help.sap.com/doc/abapdocu_750_index_htm/7.50/en-US/abenabap.htm).
I don't think they meant for their grammar be used directly by an interpreter,
but with some minor modifications I was able to make it work...


# EXAMPLE OUTPUT

Here is the result of running [loops.abap](/abippity/examples/loops.abap):

    REPORT: ZLOOPS
    ****************************************
    x: 0                                    
      y: 0                                  
      y: 1                                  
      y: 2                                  
      y: 3                                  
    x: 1                                    
    x: 2                                    
      y: 0                                  
      y: 1                                  
      y: 2                                  
      y: 3                                  
                                            
                                            
                                            
                                            
                                            
                                            
                                            
                                            
                                            
    ****************************************

In vain do you attempt to conceal your excitement.


# HOW TO USE ABIPPITY

You can run example files from the command line using [main.py](/abippity/abippity/main.py).
There are [some](/abippity/run.sh)... [example](/abippity/parse.sh)... [shellscripts](/abippity/print_keywords.sh)...
which show example usage of main.py.
(NOTE: those shellscripts expect you to `cd abippity` before running.)

Some examples of Abippity source code (which are probably valid ABAP too)
are [included in the repo](/abippity/examples/).


# HOW TO USE SAPINESS

Most of the documentation is actually in Sapiness itself:
[index.html](/sapiness/site_templates/index.html)

I was running this at [sapiness.bayersglassey.com](http://sapiness.bayersglassey.com)
for a while, but have probably taken it down by now.


To run it yourself:

    # Set up a server somewhere, with an 'abap' user.
    # Make a virtualenv called 'venv' in the abap user's home directory.
    # pip install the requirements (just Django 1.11, but see /sapiness/requirements.txt)
    # Install uwsgi under systemd.
    # Then, on your local machine, cd into this git repo and:

    export IP=...  # IP address of your server
    ./deploy.sh

...WARNING: this deployment system is not particularly robust, and these
instructions are probably not complete.
If you are the kind of person who wants to run a SAP emulator in Django,
I'm sure you'll figure out how to make it happen.


# SAPINESS SCREENSHOT

I'm proud to say no CSS or Javascript is used at all.

![](/screenshots/document.png)
![](/screenshots/output.png)
