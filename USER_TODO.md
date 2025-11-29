# User TODO

** DO NOT TOUCH OR MODIFY **

** THIS IS THE USER'S OWN TODO FILE **

* Nethack source code
    * Makefile chain? Looks broken, what is the top, and their calls?
    * unixconf.h
    * #define TEXTCOLOR
    * Check all patches
        * /* Note: tcap.h will define TERMLIB, but we undefine it in hack.h patch */
    * CO, LI
        /*
        * LI and CO are set in ioctl.c via a TIOCGWINSZ if available.  If
        * the kernel has values for either we should use them rather than
        * the values from TERMCAP ...
        */
    # ifndef MICRO
        if (!CO) CO = tgetnum("co");
        if (!LI) LI = tgetnum("li");


            getwindowsz()
        {
        #ifdef USE_WIN_IOCTL
