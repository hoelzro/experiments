#include <stdio.h>
#include <stdlib.h>

#include <X11/Xlib.h>
#include <X11/Xatom.h>
#include <X11/extensions/Xfixes.h>

#define die(msg, args...)\
    fprintf(stderr, msg "\n", ##args);\
    exit_code = 1;\
    goto cleanup;

int
main(void)
{
    int i;
    int exit_code = 0;
    Display *dsp = NULL;
    Bool status;
    int fixes_event_base, fixes_error_base;
    Window root_window;
    XEvent ev;
    Atom selection_atoms[3];
    const char *selection_atom_names[3] = {
        "PRIMARY",
        "SECONDARY",
        "CLIPBOARD",
    };

    dsp = XOpenDisplay(NULL);
    if(!dsp) {
        die("Unable to connect to X");
    }

    status = XFixesQueryExtension(dsp, &fixes_event_base, &fixes_error_base);
    if(!status) {
        die("XFixes extension missing");
    }

    root_window = RootWindow(dsp, 0);

    selection_atoms[0] = XA_PRIMARY;
    selection_atoms[1] = XA_SECONDARY;

    selection_atoms[2] = XInternAtom(dsp, "CLIPBOARD", True);
    if(selection_atoms[2] == None) {
        die("can't get CLIPBOARD atom");
    }

    for(i = 0; i < sizeof(selection_atoms)/sizeof(selection_atoms[0]); i++) {
        XFixesSelectSelectionInput(dsp, root_window, selection_atoms[i], XFixesSetSelectionOwnerNotifyMask | XFixesSelectionWindowDestroyNotifyMask | XFixesSelectionClientCloseNotifyMask);
    }

    while(1) {
        XNextEvent(dsp, &ev);

        if(ev.type >= fixes_event_base) {
            XFixesSelectionNotifyEvent *fixes_ev = (XFixesSelectionNotifyEvent *) &ev;
            const char *event_type = NULL;
            const char *selection_name = "unknown";

            switch(fixes_ev->subtype) {
                case XFixesSetSelectionOwnerNotify:
                    event_type = "XFixesSetSelectionOwnerNotify";
                    break;
                case XFixesSelectionWindowDestroyNotify:
                    event_type = "XFixesSelectionWindowDestroyNotify";
                    break;
                case XFixesSelectionClientCloseNotify:
                    event_type = "XFixesSelectionClientCloseNotify";
                    break;
            }

            for(i = 0; i < sizeof(selection_atoms)/sizeof(selection_atoms[0]); i++) {
                if(fixes_ev->selection == selection_atoms[i]) {
                    selection_name = selection_atom_names[i];
                    break;
                }
            }

            printf("Got event of type %s\n", event_type);
            printf("  Owner:     0x%x\n", fixes_ev->owner);
            printf("  Selection: %s\n", selection_name);
            printf("\n");
            fflush(stdout);
        }
    }

cleanup:
    if(dsp) {
        XCloseDisplay(dsp);
    }

    return exit_code;
}
