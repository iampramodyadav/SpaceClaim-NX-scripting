import NXOpen
import sys

the_session: NXOpen.Session = NXOpen.Session.GetSession()
base_part: NXOpen.BasePart = the_session.Parts.BaseWork
work_part: NXOpen.Part = the_session.Parts.Work
the_lw: NXOpen.ListingWindow = the_session.ListingWindow

def write(x):
    the_lw.Open()
    the_lw.WriteFullline(x)

def main():
    # the_lw.Open()
    # the_lw.WriteFullline("Starting Main() in " + the_session.ExecutingJournal)
    write("Starting Main() in " + the_session.ExecutingJournal)
    write("Hello, World!")
    write(sys.version)


if __name__ == '__main__':
    main()
