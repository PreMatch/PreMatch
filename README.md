# PreMatch

<a href="https://prematch.org">PreMatch</a> is a site that allows students at Andover High School to quickly and easily enter their schedules, and find out which of their friends are in which of their classes or lunches. Since its first launch on August 22nd, 2018, it has expanded to include a <a href="https://prematch.org/about/discord">Discord bot</a> and a <a href="https://github.com/broad-well/PreMatch-iOS">mobile app</a> that comes bundled with a widget that gives any student quick access to their schedule. The widget looks like so:

![PreMatch Widget](https://i.imgur.com/INN8wxj.png?0) 

## The Problem
Behold - the 7+H schedule system of Andover High School:

![7+H Schedule](https://i.imgur.com/d43YxsI.png)

It’s a chaotic 8-day rotation of 8 different blocks that vary in length combined with 4 lunch periods. One of these blocks is the H block, a block used for student enrichment, in which you can visit your teachers arbitrarily. When schedules are released one week before school starts, nearly every student at Andover High School goes in a frenzy, sending their schedule to everyone they know in order to see which of their friends are in which of their classes. This is a frantic, inefficient process that is never completely accurate and takes a long time. 

## Our Solution
When we, the creators of PreMatch, noticed how many students shared their schedules and the many platforms they used to share them, we decided that we had to make something that would make this process easier and more efficient, while still keeping sensitive information away from the prying eyes of the general public. 
Thus, <a href="https://prematch.org">PreMatch</a> was born. 

![PreMatch Logo](https://prematch.org/static/img/PreMatch%20Logo.png)

To use <a href="https://prematch.org">PreMatch</a>, all you need to do is visit <a href="https://prematch.org">prematch.org</a>, and log in with your **school-assigned Google account**.

![Login Page](https://i.imgur.com/E6MCYSN.png)

Next, fill in your schedule by searching for your teachers. If you would like to, you may also add in your lunch period numbers for blocks C through G.

![Inputting Schedule](https://i.imgur.com/1CKEVEN.png)

That's it! You can now view your classes and your classmates!

## Security
During the creation of <a href="https://prematch.org">PreMatch</a>, security was always one of our top concerns. We wanted to make sure that only students could access the site, and nobody else. To do this, we implemented a Google sign-in integration, which requires you to be logged into a valid *k12.andoverma.us* Google account. Without being logged into an account, all you can see is the *Home* and *About* pages. In addition, we have implemented an "invisible" setting, allowing students to only make themselves visible to their classmates, meaning that they will not show up in searches, and their own schedule will be hidden to everyone but themselves. However, they will still be visible to their classmates, but only in their shared classes. For example, if Student A and Student B share a C block class, and Student B has marked themselves as invisible, Student A will be able to see that Student B is in their C block class, but they will not be able to see any other part of their schedule. 

## Credits
<a href="https://prematch.org">PreMatch</a> was made by <a href="https://github.com/broad-well">Michael Peng</a> and <a href="https://github.com/Ivanov1ch">Daniel Ivanovich</a>, in the summer before their sophomore year. The site uses the <a href="https://bulma.io/">Bulma</a> framework and our backend is written in <a href="http://flask.pocoo.org/">Flask</a>.
The Discord Bot was programmed in Ruby using <a href="https://github.com/meew0/discordrb">discordrb</a>, and the iOS app was made using <a href="https://developer.apple.com/xcode/">Xcode</a>.
The site is hosted on <a href="https://cloud.google.com/appengine/">Google's App Engine</a>, the database is hosted on <a href="https://cloud.google.com/datastore/">Google's Cloud Datastore</a>, and the Discord bot is run on <a href="https://cloud.google.com/compute/">Google's Compute Engine</a>.
