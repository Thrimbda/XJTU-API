# little-spider-big-net
> this is a spider for myself to practice under MIT Licence.

### require
mySpider is build on bs4 and requests using python3 programming lauguage.
### what can it do?
for now I'm using it do something with my uni's website.
it can also do normal grab things like other spiders do.
* get your teaching assess(see usage below)
* get your schedule(form of python list object)
    * use schedule() method to generate your schedule object.
    * use schedule and timetable(time available) derictly.

    ##### example:
        XJTUSpider('ssfw').scheduleModule.schedule.schedule
        XJTUSpider('ssfw').scheduleModule.schedule.timetable

### usage
* Teaching assess(auto only for now)
    1. touch a new file named "main.py"(or anything you want, name doesn't matter).
    2. instantiated a XJTUSpider with string param 'ssfw'
    3. login
    4. use method XJTUSpider.teachingAssess()
    5. done!

    ##### example:
        mySpider = XJTUSpider('ssfw')
        mySpider.login(username='YOUR_USER_NAME', password='YOUR_PASS_WORD')
        mySpider.teachingAssess() # auto assess mode. or use specific assess mod
        # mySpider.teachingAssess(autoMode=False, index=0, fraction=[5,5,5,5,5,5,5,5,5,4], pgyj='YOUR_ASSESS_IDEA', ztpj='YOUR_SAMMARY')
        mySpider.logout()

    ##### **XJTUSpider.teachingAssess(self, autoMode=True, index=None, fraction=None, pgyj=None, ztpj=None)**
    if auto mode is true, then you'd place noting in the method.
    if not, then declare autoMode=False and give the mothod index of assessment, fraction, idea and sammary.
    **Don't worry if you got no index and assessments info**
    just don't give the method the info you don't know, it will list options for you.

    like this:

        mySpider.teachingAssess(autoMode=False)
    will print and return assessments for you.

        mySpider.teachingAssess(autoMode=False, index=0)
    will print and return fraction options for you.

### problem
source code of this spider is not very pythonic.
I'm trying to use OOP but still, it looks bad. Because I'm a starter.
if you have any idea of how to improve it. please tell me!
### blueprint
make it a XJTU API first.
* will be capable doing anything on it with XJTU sites.
* will be the base work of any further XJTU application.
* free to use under MIT License.

I will working on it enduringly.
To make it a spider framework with some good design patterns.