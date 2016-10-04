# little-spider-big-net
> this is a spider for myself to practice under MIT Licence.

### require
mySpider is build on bs4 and requests using python3 programming lauguage.
### what can it do?
for now I'm using it do something with my uni's website.
it can also do normal grab things like other spiders do.
### usage
* Teaching assess(auto only for now)
    1. touch a new file named "main.py"(or anything you want, name doesn't matter).
    2. instantiated a XJTUSpider with string param 'ssfw'
    3. login
    4. use method teachingAssess
    5. done!

    ##### example:
        mySpider = XJTUSpider('ssfw')
        mySpider.login(username='YOUR_USER_NAME', password='YOUR_PASS_WORD')
        mySpider.teachingAssess()
        mySpider.logout()

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